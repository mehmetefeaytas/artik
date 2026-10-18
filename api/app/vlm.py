"""EVREN LLM API görsel sınıflandırıcı (Türkiye ulusal LLM altyapısı).

CLIP'in belirsiz kaldığı maskelerde (ör. tabak + yemek birleşik kaba maskeler)
görsel-anlayan modelle (VLM) arabuluculuk yapar. API erişilemezse sessizce
devre dışı kalır; pipeline CLIP ile çalışmaya devam eder.

Yapılandırma (ortam değişkenleri veya api/.env):
  EVREN_API_KEY   — anahtar (zorunlu)
  EVREN_MODEL     — model (varsayılan: qwen3-vl-30b)
  EVREN_TIMEOUT   — saniye (varsayılan: 90)
"""

from __future__ import annotations

import base64
import io
import json
import os
import urllib.request
from pathlib import Path

from PIL import Image

BASE_URL = "https://evren-llmapi.ssyz.org.tr/v1"
DEFAULT_MODEL = "qwen3-vl-30b"

DISTRACTOR_LABEL = "__distraktor__"
DISTRACTOR_TEXT = "boş tabak, çatal-kaşık-bıçak, bardak, tepsi, peçete, masa ya da arka plan"


def _load_env_file() -> None:
    """api/.env dosyasını (varsa) os.environ'a yükler — bağımlılıksız."""
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _to_data_url(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="JPEG", quality=88)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


class EvrenVLM:
    """Toplu kırpım sınıflandırıcı: tek çağrıda N görüntüyü etiketler."""

    def __init__(self) -> None:
        _load_env_file()
        self.api_key = os.environ.get("EVREN_API_KEY", "")
        self.model = os.environ.get("EVREN_MODEL", DEFAULT_MODEL)
        self.timeout = float(os.environ.get("EVREN_TIMEOUT", "90"))
        self.enabled = bool(self.api_key)

    # ------------------------------------------------------------------ call

    def classify_crops(
        self, crops: list[Image.Image], menu_labels: list[str]
    ) -> list[str | None] | None:
        """Her kırpım için menü etiketi, DISTRACTOR_LABEL ya da None döndür.

        Başarısızlıkta (ağ/zaman aşımı) None döner; çağıran CLIP kararına döner.
        """
        if not self.enabled or not crops:
            return None
        options = "\n".join(f"- {label}" for label in menu_labels) + f"\n- {DISTRACTOR_TEXT}"
        content: list[dict] = []
        for i, crop in enumerate(crops):
            content.append({"type": "text", "text": f"Görüntü {i}:"})
            content.append({"type": "image_url", "image_url": {"url": _to_data_url(crop)}})
        content.append(
            {
                "type": "text",
                "text": (
                    "Her görüntü bir üniversite yemekhanesi tepsisi kırpımıdır. "
                    "Her görüntü için görüntüde BASKIN olan tek şeyi aşağıdaki "
                    "seçeneklerden BİREBİR aynı yazıyla seç:\n"
                    f"{options}\n"
                    "Kurallar: Yeni etiket uydurma. Açıklama yazma. Yanıt SADECE "
                    "şu biçimde geçerli JSON olsun: "
                    '{"0": "seçilen etiket", "1": "seçilen etiket"} — anahtarlar '
                    "görüntü numaralarıdır."
                ),
            }
        )
        payload = {
            "model": self.model,
            "max_tokens": 2048,
            "temperature": 0,
            "messages": [{"role": "user", "content": content}],
        }
        req = urllib.request.Request(
            f"{BASE_URL}/chat/completions",
            data=json.dumps(payload).encode(),
            headers={"X-API-Key": self.api_key, "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                data = json.loads(r.read())
            text = data["choices"][0]["message"]["content"].strip()
            # Model bazen kod bloğuna sarar
            if text.startswith("```"):
                text = text.strip("`")
                if text.startswith("json"):
                    text = text[4:]
            start, end = text.find("{"), text.rfind("}")
            if start >= 0 and end > start:
                text = text[start : end + 1]
            parsed = json.loads(text)
            out: list[str | None] = []
            for i in range(len(crops)):
                label = parsed.get(str(i))
                out.append(label.strip() if isinstance(label, str) else None)
            return out
        except Exception:
            return None

    def label_to_menu_key(
        self, label: str | None, menu: list[dict]
    ) -> dict | None:
        """VLM etiketini menü öğesine çevirir; distraktör/variantsızsa None.

        Birden çok eşleşme varsa en uzun ad kazanır ("Salata" <
        "Deniz Ürünü Salatası" karışıklığını önler).
        """
        if not label:
            return None
        norm = label.strip().lower()
        best: tuple[int, dict] | None = None
        for it in menu:
            for name in {it["name_tr"].lower(), it["name_en"].lower()}:
                # birebir ya da içerme eşleşmesi ("fasulye tabağı" → "Fasulye")
                if norm == name or name in norm or norm in name:
                    if best is None or len(name) > best[0]:
                        best = (len(name), it)
        if best is not None:
            it = best[1]
            return {"key": it["key"], "name_tr": it["name_tr"], "score": 0.8, "vlm": True}
        return {"key": DISTRACTOR_LABEL, "name_tr": label, "score": 0.0, "vlm": True}
