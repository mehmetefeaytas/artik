"""Gerçek veri setiyle doğrulama (UNIMIB/Padova tepsi çiftleri).

Her tepsi için: servis (food_image) ve 3 artık (leftover1..3) fotoğrafı,
yemek-ID etiketli ground-truth maskelerle gelir. Bu script:

1. Maskelerden her yemeğin GERÇEK artık oranını hesaplar
   (alan(sonra, ID) / alan(önce, ID))
2. ARTIK pipeline'ını aynı çift üzerinde çalıştırır
3. Öğe bazında tahmin-gerçek karşılaştırması ve toplu metrikler üretir

Kullanım (api/ altından):  uv run python scripts/validate_real.py [--trays 1,2] [--states 2]
Çıktı: demo/real_dataset/val_results.json + konsol tablosu
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.overlay import annotate
from app.vision import TrayAnalyzer

ROOT = Path(__file__).resolve().parent.parent.parent
DS = ROOT / "demo" / "real_dataset"

# ID → (name_tr, name_en, CLIP prompt, porsiyon_g)
FOODS: dict[int, dict] = {
    1: {"key": "pesto_makarna", "name_tr": "Pesto Makarna", "name_en": "pasta with pesto",
        "clip_prompt": "a plate of pasta with green pesto sauce", "portion_g": 200},
    2: {"key": "domates_makarna", "name_tr": "Domates Soslu Makarna",
        "name_en": "pasta with tomato sauce",
        "clip_prompt": "a plate of pasta with tomato sauce", "portion_g": 200},
    3: {"key": "bolognez_makarna", "name_tr": "Bolognez Makarna",
        "name_en": "pasta with meat sauce",
        "clip_prompt": "a plate of pasta with bolognese meat sauce", "portion_g": 200},
    4: {"key": "midyeli_makarna", "name_tr": "Midye İstiridyeli Makarna",
        "name_en": "pasta with clams and mussels",
        "clip_prompt": "a plate of pasta with clams and mussels", "portion_g": 200},
    5: {"key": "sebzeli_pilav", "name_tr": "Sebzeli Pirinç Pilavı",
        "name_en": "pilaw rice with peppers and peas",
        "clip_prompt": "a plate of pilaw rice with peppers and peas", "portion_g": 180},
    6: {"key": "izgara_pirzola", "name_tr": "Izgara Pirzola", "name_en": "grilled pork cutlet",
        "clip_prompt": "a grilled pork cutlet on a plate", "portion_g": 180},
    7: {"key": "balik_fileto", "name_tr": "Balık Fileto", "name_en": "fish cutlet",
        "clip_prompt": "a breaded fish cutlet on a plate", "portion_g": 180},
    8: {"key": "tavsan", "name_tr": "Tavşan Eti", "name_en": "rabbit",
        "clip_prompt": "cooked rabbit meat with sauce on a plate", "portion_g": 200},
    9: {"key": "deniz_salata", "name_tr": "Deniz Ürünü Salatası", "name_en": "seafood salad",
        "clip_prompt": "a plate of seafood salad", "portion_g": 150},
    10: {"key": "fasulye", "name_tr": "Fasulye", "name_en": "beans",
         "clip_prompt": "a plate of cooked white beans", "portion_g": 150},
    11: {"key": "feslegenli_patates", "name_tr": "Fesleğenli Patates", "name_en": "basil potatoes",
         "clip_prompt": "a plate of potatoes with basil", "portion_g": 150},
    12: {"key": "salata", "name_tr": "Salata", "name_en": "salad",
         "clip_prompt": "a plate of fresh green salad", "portion_g": 100},
    13: {"key": "ekmek", "name_tr": "Ekmek", "name_en": "bread",
         "clip_prompt": "a piece of bread", "portion_g": 60},
}


def tray_ids(tray: int) -> list[int]:
    txt = (DS / f"tray{tray}" / "bounding_boxes" / "food_image_bounding_box.txt").read_text()
    return sorted({int(line.split(":")[1].split(";")[0]) for line in txt.strip().splitlines()})


def mask_areas(tray: int, which: str) -> dict[int, int]:
    path = DS / f"tray{tray}" / "masks" / f"{which}.png"
    m = np.array(Image.open(path))
    out: dict[int, int] = {}
    for fid in np.unique(m):
        if fid == 0:
            continue
        out[int(fid)] = int((m == fid).sum())
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--trays", default="1,2,3,4,5,6,7,8")
    ap.add_argument("--states", default="1,2,3")
    ap.add_argument("--save-overlays", action="store_true")
    args = ap.parse_args()

    trays = [int(t) for t in args.trays.split(",")]
    states = [int(s) for s in args.states.split(",")]

    analyzer = TrayAnalyzer()
    records: list[dict] = []

    for tray in trays:
        ids = tray_ids(tray)
        menu = [FOODS[i] for i in ids]
        before_img = Image.open(DS / f"tray{tray}" / "food_image.jpg")
        areas_b = mask_areas(tray, "food_image_mask")

        for st in states:
            t0 = time.time()
            after_img = Image.open(DS / f"tray{tray}" / f"leftover{st}.jpg")
            areas_a = mask_areas(tray, f"leftover{st}")

            result = analyzer.analyze_pair(before_img, after_img, menu)
            dt = time.time() - t0

            est = {i["key"]: i for i in result["items"]}
            for fid in ids:
                f = FOODS[fid]
                ab, aa = areas_b.get(fid, 0), areas_a.get(fid, 0)
                gt = (aa / ab) if ab > 0 else None
                if gt is not None:
                    gt = min(gt, 1.0)
                item = est.get(f["key"])
                pred = item["leftover_ratio"] if item else None
                conf = item["clip_confidence"] if item else None
                records.append(
                    {
                        "tray": tray, "state": st, "food_id": fid,
                        "name_tr": f["name_tr"],
                        "gt_ratio": round(gt, 3) if gt is not None else None,
                        "pred_ratio": pred,
                        "abs_err": round(abs(pred - gt), 3)
                        if (pred is not None and gt is not None) else None,
                        "detected": item is not None,
                        "clip_confidence": conf,
                    }
                )
                print(  # noqa: T201
                    f"t{tray} L{st} {f['name_tr']:<24} gt={gt if gt is None else round(gt, 2)} "
                    f"pred={pred if pred is None else round(pred, 2)} "
                    f"{'BULUNAMADI' if pred is None else ''}"
                )
            if args.save_overlays:
                order = [m["key"] for m in menu]
                (DS / f"tray{tray}").joinpath(f"overlay_L{st}_before.png").write_bytes(
                    annotate(before_img, result.pop("segments_before"), order, f"TRAY {tray} ÖNCE")
                )
                (DS / f"tray{tray}").joinpath(f"overlay_L{st}_after.png").write_bytes(
                    annotate(
                        after_img, result.pop("segments_after"), order,
                        f"TRAY {tray} SONRA L{st}",
                    )
                )
            else:
                result.pop("segments_before"), result.pop("segments_after")
            print(f"  → {dt:.0f} sn")  # noqa: T201

    matched = [r for r in records if r["abs_err"] is not None]
    detected = [r for r in records if r["detected"]]
    mae = sum(r["abs_err"] for r in matched) / len(matched) if matched else None
    summary = {
        "pairs": len(trays) * len(states),
        "item_evaluations": len(records),
        "detection_rate": round(len(detected) / len(records), 3),
        "matched_evaluations": len(matched),
        "mae_ratio": round(mae, 3) if mae is not None else None,
        "source": "UNIMIB/Padova gerçek yemekhane tepsileri (demo/real_dataset)",
        "gt_method": "piksel maskelerinden alan oranı",
    }
    print("\n=== ÖZET ===")  # noqa: T201
    for k, v in summary.items():
        print(f"{k}: {v}")  # noqa: T201

    out = {"summary": summary, "records": records}
    (DS / "val_results.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print("yazıldı: demo/real_dataset/val_results.json")  # noqa: T201


if __name__ == "__main__":
    main()
