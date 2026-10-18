"""Teşhis: bir görüntüdeki tüm SAM maskeleri + CLIP top-3 sınıf olasılıkları."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image

from app.vision import DISTRACTOR_PROMPTS, TrayAnalyzer, preprocess

ROOT = Path(__file__).resolve().parent.parent.parent
PAIR = ROOT / "demo" / "test_pairs"

MENU = [
    {
        "key": "mercimek_corbasi",
        "name_tr": "Mercimek Çorbası",
        "name_en": "red lentil soup",
        "clip_prompt": "a creamy bowl of orange turkish lentil soup",
        "portion_g": 250,
    },
    {
        "key": "kuru_fasulye",
        "name_tr": "Kuru Fasulye",
        "name_en": "white bean stew",
        "clip_prompt": "a plate of stewed white beans, individual beans visible in red sauce",
        "portion_g": 280,
    },
    {
        "key": "pirinc_pilavi",
        "name_tr": "Pirinç Pilavı",
        "name_en": "rice pilaf",
        "clip_prompt": "a plate of turkish rice pilaf",
        "portion_g": 180,
    },
    {
        "key": "coban_salata",
        "name_tr": "Çoban Salata",
        "name_en": "shepherd's salad",
        "clip_prompt": "a plate of fresh vegetable salad with tomatoes and cucumber",
        "portion_g": 150,
    },
]

def dump(analyzer: TrayAnalyzer, path: Path, menu: list[dict]) -> None:
    img = preprocess(Image.open(path))
    masks = analyzer._sam_masks(img)
    print(f"\n=== {path.name} — {len(masks)} maske (alan filtresi sonrası) ===")  # noqa: T201

    prompts = [f"a photo of {it['name_en']}" for it in menu] + DISTRACTOR_PROMPTS
    text_feats = analyzer._clip_text_feats(prompts)

    import torch

    crops = [analyzer._masked_crop(img, m) for m in masks]
    if not crops:
        return
    inputs = analyzer.clip_processor(images=crops, return_tensors="pt")
    inputs = {k: v.to(analyzer.device) for k, v in inputs.items()}
    with torch.no_grad():
        out = analyzer.clip.get_image_features(**inputs)
    f = out if torch.is_tensor(out) else out.pooler_output
    f = f / f.norm(dim=-1, keepdim=True)
    scale = analyzer.clip.logit_scale.detach().exp().to(f.device)
    probs = ((f @ text_feats.T) * scale).float().softmax(dim=-1).cpu().numpy()

    for m, row in zip(masks, probs):
        x, y, w, h = (int(v) for v in m["bbox"])
        area = m["area"] / (img.width * img.height)
        top3 = sorted(enumerate(row), key=lambda t: -t[1])[:3]
        tops = ", ".join(f"{prompts[i][:28]}={p:.2f}" for i, p in top3)
        print(f"  alan={area:.3f} bbox=({x},{y},{w},{h}) | {tops}")  # noqa: T201


def main() -> None:
    a = TrayAnalyzer()
    dump(a, PAIR / "pair1_before.png", MENU)
    dump(a, PAIR / "pair1_after.png", MENU)


if __name__ == "__main__":
    main()
