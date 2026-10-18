"""Pipeline doğrulama: sahnepair üzerinde ground truth ile karşılaştırma.

Kullanım (api/ altından):  uv run python scripts/test_pipeline.py
Çıktılar: demo/test_pairs/overlay_before.png, overlay_after.png, sonuc.json
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image

from app.overlay import annotate
from app.vision import TrayAnalyzer

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


def main() -> None:
    t0 = time.time()
    analyzer = TrayAnalyzer()
    print(f"model yükleme: {time.time() - t0:.1f}s | cihaz: {analyzer.device}")  # noqa: T201

    before = Image.open(PAIR / "pair1_before.png")
    after = Image.open(PAIR / "pair1_after.png")

    t1 = time.time()
    result = analyzer.analyze_pair(before, after, MENU)
    dt = time.time() - t1
    print(f"analiz: {dt:.1f}s")  # noqa: T201

    gt = json.loads((PAIR / "pair1_ground_truth.json").read_text())["keep_ratios"]
    print("\n--- öğe sonuçları (gt = sahnelenen gerçek oran) ---")  # noqa: T201
    for it in result["items"]:
        g = gt.get(it["key"])
        err = abs(it["leftover_ratio"] - g) if g is not None else None
        print(  # noqa: T201
            f"{it['name_tr']:<18} tahmin={it['leftover_ratio']:.3f}"
            f" gt={g:.2f} hata={err:.3f} conf={it['clip_confidence']:.2f}"
        )
    print(f"\nuyarılar: {result['warnings']}")  # noqa: T201
    print(f"toplam tahmini artık: {result['total_estimated_leftover_g']} g")  # noqa: T201

    order = [m["key"] for m in MENU]
    (PAIR / "overlay_before.png").write_bytes(
        annotate(before, result.pop("segments_before"), order, "ÖNCE — servis")
    )
    (PAIR / "overlay_after.png").write_bytes(
        annotate(after, result.pop("segments_after"), order, "SONRA — iade")
    )
    result["latency_s"] = round(dt, 1)
    result["device"] = analyzer.device
    (PAIR / "sonuc.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=1, default=str), encoding="utf-8"
    )
    print("overlay + sonuc.json yazıldı")  # noqa: T201


if __name__ == "__main__":
    main()
