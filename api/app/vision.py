"""Zero-shot tepsi analizi: SAM segmentasyonu + CLIP sınıflandırması.

Prensip: görüntüden elde edilen her değer TAHMİNDİR.
- Artık oranı = (sonra görüntüdeki yemek alanı) / (önce görüntüdeki yemek alanı)
- Tahmini artık gram = standart porsiyon gramı x artık oranı
Kesin kütle için tartım doğrulaması gerekir (bkz. /yontem sayfası).
"""

from __future__ import annotations

import os
import urllib.request
from dataclasses import dataclass

import numpy as np
import torch
from PIL import Image, ImageOps

from .vlm import DISTRACTOR_LABEL, EvrenVLM

SAM_URL = "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth"
_CHECKPOINT_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "checkpoints", "sam_vit_b_01ec64.pth")
)
CLIP_MODEL_ID = "openai/clip-vit-base-patch32"

MAX_SIDE = 768
MIN_AREA_FRAC = 0.004
MAX_AREA_FRAC = 0.45
MIN_CLIP_PROB = 0.25
DISTRACTOR_MARGIN = 0.05
# CLIP belirsizlik bölgesi: VLM arabuluculuğuna (EVREN) gönderilecek maskeler
VLM_REJECT_PROB = 0.10
VLM_CLEAR_MARGIN = 0.25
RATIO_CLAMP = 1.2
POINTS_PER_SIDE = int(os.environ.get("ARTIK_SAM_POINTS", "24"))

DISTRACTOR_PROMPTS = [
    "an empty white plate",
    "an empty bowl",
    "a metal fork",
    "a metal spoon",
    "a knife",
    "a drinking glass",
    "a cafeteria tray",
    "a paper napkin",
    "a human hand",
    "a dining table",
]


def _ensure_sam_checkpoint() -> str:
    if os.path.exists(_CHECKPOINT_PATH):
        return _CHECKPOINT_PATH
    os.makedirs(os.path.dirname(_CHECKPOINT_PATH), exist_ok=True)
    print(f"SAM checkpoint indiriliyor: {SAM_URL}")  # noqa: T201
    urllib.request.urlretrieve(SAM_URL, _CHECKPOINT_PATH)
    return _CHECKPOINT_PATH


def _pick_device() -> str:
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def preprocess(image: Image.Image) -> Image.Image:
    """EXIF düzelt + uzun kenarı MAX_SIDE'e ölçekle."""
    img = ImageOps.exif_transpose(image).convert("RGB")
    w, h = img.size
    scale = MAX_SIDE / max(w, h)
    if scale < 1:
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    return img


@dataclass
class TraySegment:
    key: str
    name_tr: str
    score: float
    area_frac: float
    bbox: tuple[int, int, int, int]
    mask: np.ndarray


class TrayAnalyzer:
    """Öğrenme gerektirmeyen (zero-shot) tepsi analizcisi.

    Menü etiketleri istekle geldiği için her yemekhane menüsüne uyarlanabilir;
    model eğitimi gerekmez. Bu bir bilinçli tasarım tercihidir (bkz. model kartı).
    """

    def __init__(self) -> None:
        from segment_anything import SamAutomaticMaskGenerator, sam_model_registry

        self.device = _pick_device()
        # SAM CPU'da: MPS, segment_anything'in float64 nokta girdisini desteklemiyor.
        sam = sam_model_registry["vit_b"](checkpoint=_ensure_sam_checkpoint())
        sam.to(device="cpu")
        self.mask_generator = SamAutomaticMaskGenerator(
            sam,
            points_per_side=POINTS_PER_SIDE,
            pred_iou_thresh=0.86,
            stability_score_thresh=0.90,
            box_nms_thresh=0.7,
            min_mask_region_area=1500,
        )

        from transformers import CLIPModel, CLIPProcessor

        self.clip = CLIPModel.from_pretrained(CLIP_MODEL_ID).to(self.device)
        self.clip.eval()
        self.clip_processor = CLIPProcessor.from_pretrained(CLIP_MODEL_ID)
        # EVREN VLM arabulucu (anahtar yoksa devre dışı; CLIP tek başına çalışır)
        self.vlm = EvrenVLM()

    # ------------------------------------------------------------------ SAM

    def _sam_masks(self, image: Image.Image) -> list[dict]:
        arr = np.asarray(image)
        masks = self.mask_generator.generate(arr)
        h, w = arr.shape[:2]
        total = float(h * w)
        out = []
        for m in masks:
            frac = float(m["area"]) / total
            if MIN_AREA_FRAC <= frac <= MAX_AREA_FRAC:
                out.append(m)
        return out

    # ----------------------------------------------------------------- CLIP

    def _clip_text_feats(self, prompts: list[str]) -> torch.Tensor:
        inputs = self.clip_processor(text=prompts, return_tensors="pt", padding=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        with torch.no_grad():
            out = self.clip.get_text_features(**inputs)
        feats = out if torch.is_tensor(out) else out.pooler_output
        return feats / feats.norm(dim=-1, keepdim=True)

    def _classify_masks(
        self, image: Image.Image, masks: list[dict], menu: list[dict]
    ) -> list[dict | None]:
        """Her maske için menü etiketi ya da None (menü dışı / tabak / çatal...).

        Her maske İKİ kırpımla sınıflanır: (a) maske dışı griye boyanmış kırpım,
        (b) düz bbox kırpımı (tabak bağlamıyla birleşik maskeler için).
        Sınıf başına iki kırpımın olasılığının en büyüğü esas alınır.
        """
        if not masks:
            return []

        def prompt_for(it: dict) -> str:
            return it.get("clip_prompt") or f"a photo of {it['name_en']}"

        prompts = [prompt_for(it) for it in menu] + DISTRACTOR_PROMPTS
        text_feats = self._clip_text_feats(prompts)

        crops = []
        for m in masks:
            crops.append(self._masked_crop(image, m))
            crops.append(self._bbox_crop(image, m))
        inputs = self.clip_processor(images=crops, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        with torch.no_grad():
            out = self.clip.get_image_features(**inputs)
        img_feats = out if torch.is_tensor(out) else out.pooler_output
        img_feats = img_feats / img_feats.norm(dim=-1, keepdim=True)
        # CLIP'in öğrenilmiş sıcaklığıyla ölçekle (yoksa softmax düzleşir)
        scale = self.clip.logit_scale.detach().exp().to(img_feats.device)
        probs = ((img_feats @ text_feats.T) * scale).float().softmax(dim=-1).cpu().numpy()

        n_menu = len(menu)
        results: list[dict | None] = []
        ambiguous: list[int] = []
        for i, m in enumerate(masks):
            row_masked = probs[2 * i]
            row_bbox = probs[2 * i + 1]
            row = np.maximum(row_masked, row_bbox)
            menu_p, dist_p = row[:n_menu], row[n_menu:]
            best_menu = int(menu_p.argmax())
            best_dist = float(dist_p.max())
            p = float(menu_p[best_menu])
            if p > MIN_CLIP_PROB and p - best_dist > DISTRACTOR_MARGIN:
                it = menu[best_menu]
                results.append({"key": it["key"], "name_tr": it["name_tr"], "score": p})
            elif p < VLM_REJECT_PROB or (best_dist - p) > VLM_CLEAR_MARGIN:
                results.append(None)  # belirgin şekilde menü dışı — VLM'e gerek yok
            else:
                results.append(None)  # aşağıda VLM arabuluculuğu doldurur
                ambiguous.append(i)

        # --- EVREN VLM arabuluculuğu: CLIP'in belirsiz kaldığı maskeler ---
        if ambiguous and self.vlm.enabled:
            crops = [self._bbox_crop(image, masks[i]) for i in ambiguous]
            menu_labels = [it["name_tr"] for it in menu]
            labels = self.vlm.classify_crops(crops, menu_labels)
            if labels is not None:
                for idx, label in zip(ambiguous, labels):
                    res = self.vlm.label_to_menu_key(label, menu)
                    if res is not None and res["key"] != DISTRACTOR_LABEL:
                        results[idx] = res
            # labels None (ağ hatası) → CLIP kararı (reddet) geçerli kalır
        return results

    @staticmethod
    def _masked_crop(image: Image.Image, mask_data: dict) -> Image.Image:
        """Maskeyi bbox + dolgu ile kırp; maske dışı nötr gri olur (CLIP girdisi)."""
        mask = mask_data["segmentation"]
        x, y, w, h = (int(v) for v in mask_data["bbox"])  # SAM bbox: XYWH
        x0, y0, x1, y1 = x, y, x + w, y + h
        pad_x = max(2, int((x1 - x0) * 0.12))
        pad_y = max(2, int((y1 - y0) * 0.12))
        cx0, cy0 = max(0, x0 - pad_x), max(0, y0 - pad_y)
        cx1, cy1 = min(image.width, x1 + pad_x), min(image.height, y1 + pad_y)
        if cx1 - cx0 < 4 or cy1 - cy0 < 4:
            cx0, cy0, cx1, cy1 = 0, 0, image.width, image.height

        sub = mask[cy0:cy1, cx0:cx1]
        crop = image.crop((cx0, cy0, cx1, cy1)).copy()
        gray = Image.new("RGB", crop.size, (124, 124, 124))
        crop.paste(gray, (0, 0), Image.fromarray((~sub).astype(np.uint8) * 255))
        return crop

    @staticmethod
    def _bbox_crop(image: Image.Image, mask_data: dict) -> Image.Image:
        """Düz bbox kırpımı (tabak + yemek bağlamı)."""
        x, y, w, h = (int(v) for v in mask_data["bbox"])  # SAM bbox: XYWH
        pad_x = max(2, int(w * 0.12))
        pad_y = max(2, int(h * 0.12))
        cx0, cy0 = max(0, x - pad_x), max(0, y - pad_y)
        cx1, cy1 = min(image.width, x + w + pad_x), min(image.height, y + h + pad_y)
        if cx1 - cx0 < 4 or cy1 - cy0 < 4:
            return image.copy()
        return image.crop((cx0, cy0, cx1, cy1)).copy()

    # ------------------------------------------------------------- segments

    def segments(self, image: Image.Image, menu: list[dict]) -> list[TraySegment]:
        img = preprocess(image)
        masks = self._sam_masks(img)
        labels = self._classify_masks(img, masks, menu)
        segs: list[TraySegment] = []
        for m, lab in zip(masks, labels):
            if lab is None:
                continue
            x, y, w, h = (int(v) for v in m["bbox"])  # SAM bbox: XYWH
            segs.append(
                TraySegment(
                    key=lab["key"],
                    name_tr=lab["name_tr"],
                    score=lab["score"],
                    area_frac=float(m["area"]) / (img.width * img.height),
                    bbox=(x, y, x + w, y + h),
                    mask=m["segmentation"],
                )
            )
        return _merge_same_label(segs)

    # ---------------------------------------------------------------- pair

    def analyze_pair(
        self, before: Image.Image, after: Image.Image, menu: list[dict]
    ) -> dict:
        b_segs = self.segments(before, menu)
        a_segs = self.segments(after, menu)

        # Aynı etiketin (dedup sonrası) ayrık parçalarının alanları toplanır;
        # SAM bazen bir yemeği parçalara böler.
        areas_b: dict[str, float] = {}
        for s in b_segs:
            areas_b[s.key] = areas_b.get(s.key, 0.0) + s.area_frac
        areas_a: dict[str, float] = {}
        for s in a_segs:
            areas_a[s.key] = areas_a.get(s.key, 0.0) + s.area_frac

        items, warnings = [], []
        for it in menu:
            key = it["key"]
            if key not in areas_b:
                if key in areas_a:
                    warnings.append(
                        f"{it['name_tr']}: önce görüntüde tespit edilemedi (sonra görüntüde var)."
                    )
                continue
            ab, aa = areas_b[key], areas_a.get(key, 0.0)
            ratio = aa / ab if ab > 0 else 0.0
            if ratio > RATIO_CLAMP:
                warnings.append(
                    f"{it['name_tr']}: sonra görüntüde öncekinden fazla alan tespit edildi "
                    f"(oran {ratio:.2f}); oran 1.0'a sabitlendi."
                )
                ratio = 1.0
            portion = it.get("portion_g")
            est_g = round(portion * ratio, 1) if portion else None
            conf = max((s.score for s in b_segs + a_segs if s.key == key), default=0.0)
            items.append(
                {
                    "key": key,
                    "name_tr": it["name_tr"],
                    "name_en": it["name_en"],
                    "before_area_frac": round(ab, 5),
                    "after_area_frac": round(aa, 5),
                    "leftover_ratio": round(ratio, 3),
                    "leftover_pct": round(ratio * 100),
                    "estimated_leftover_g": est_g,
                    "portion_g": portion,
                    "clip_confidence": round(conf, 3),
                }
            )

        total_g = round(sum(i["estimated_leftover_g"] or 0 for i in items), 1)
        matched = len(items)
        return {
            "items": items,
            "matched_items": matched,
            "total_estimated_leftover_g": total_g,
            "warnings": warnings,
            "note": "Görüntüden alan oranıyla tahmin; tartım doğrulaması gerekir.",
            "segments_before": b_segs,
            "segments_after": a_segs,
        }


def _iou(a: np.ndarray, b: np.ndarray) -> float:
    inter = np.logical_and(a, b).sum()
    union = np.logical_or(a, b).sum()
    return float(inter / union) if union > 0 else 0.0


def _contained(a: np.ndarray, b: np.ndarray) -> bool:
    """Küçük maske büyükün içindeyse (kapsama oranı > 0.6)."""
    inter = np.logical_and(a, b).sum()
    smaller = min(a.sum(), b.sum())
    return smaller > 0 and inter / smaller > 0.6


def _merge_same_label(segs: list[TraySegment]) -> list[TraySegment]:
    """Aynı etiketli örtüşen/kapsanan maskeleri ele (SAM bazen aynı yemeği böler)."""
    kept: list[TraySegment] = []
    for s in sorted(segs, key=lambda s: s.area_frac, reverse=True):
        dup = any(
            s.key == k.key and (_iou(s.mask, k.mask) > 0.5 or _contained(s.mask, k.mask))
            for k in kept
        )
        if not dup:
            kept.append(s)
    return kept
