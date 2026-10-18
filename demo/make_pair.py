"""Kompozit test tepsi çiftleri (before/after) üretir.

Amaç: SAM+CLIP pipeline'ını bilinen (ground-truth) artık oranlarıyla doğrulamak.
After tabağındaki yemek, before'unkinin keep oranının kareköğü kadar ölçeklenir;
alan oranı = keep olduğu için pipeline'ın ölçtüğü oran doğrudan karşılaştırılabilir.

Bu görüntüler SAHNELENMİŞTİR; gerçek yemekhane çekimi değildir.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).parent
FOOD = HERE / "sample_food"
OUT = HERE / "test_pairs"

TRAY_SIZE = (960, 700)
TRAY_COLOR = (108, 122, 137)
PLATE_R = 130

# (dosya, anahtar, isim_tr, isim_en, portion_g, keep_ratio, rotasyon)
FOODS = [
    ("mercimek_corbasi.jpg", "mercimek_corbasi", "Mercimek Çorbası", "red lentil soup", 250, 0.05, 4),
    ("kuru_fasulye.jpg", "kuru_fasulye", "Kuru Fasulye", "white bean stew", 280, 0.62, 6),
    ("pirinc_pilavi.jpg", "pirinc_pilavi", "Pirinç Pilavı", "rice pilaf", 180, 0.15, 5),
    ("coban_salata.jpg", "coban_salata", "Çoban Salata", "shepherd's salad", 150, 0.85, 0),
]

PLATE_POS = [(180, 180), (480, 180), (180, 490), (480, 490)]


def circular_food(path: Path, diameter: int, rotate: float = 0.0) -> Image.Image:
    img = Image.open(path).convert("RGB")
    w, h = img.size
    side = min(w, h)
    img = img.crop(((w - side) // 2, (h - side) // 2, (w + side) // 2, (h + side) // 2))
    img = img.resize((diameter, diameter), Image.LANCZOS)
    if rotate:
        img = img.rotate(rotate, resample=Image.BICUBIC, fillcolor=None)
    mask = Image.new("L", (diameter, diameter), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, diameter, diameter], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(2))
    out = Image.new("RGBA", (diameter, diameter), (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    return out


def make_tray(keep: bool) -> Image.Image:
    import math

    tray = Image.new("RGB", TRAY_SIZE, (222, 226, 230))
    d = ImageDraw.Draw(tray, "RGBA")
    d.rounded_rectangle(
        [24, 24, TRAY_SIZE[0] - 24, TRAY_SIZE[1] - 24], radius=40, fill=TRAY_COLOR
    )
    for (cx, cy), (fname, _, _, _, _, keep_ratio, rot) in zip(PLATE_POS, FOODS):
        d.ellipse(
            [cx - PLATE_R, cy - PLATE_R, cx + PLATE_R, cy + PLATE_R],
            fill=(245, 245, 240),
            outline=(210, 210, 205),
            width=3,
        )
        if keep:
            scale = math.sqrt(keep_ratio)
            diam = int(2 * PLATE_R * 0.88 * scale)
            if diam < 8:
                continue  # tamamen yenmiş
            food = circular_food(FOOD / fname, diam, rotate=rot + 3)
            tray.paste(food, (cx - diam // 2, cy - diam // 2), food)
        else:
            diam = int(2 * PLATE_R * 0.88)
            food = circular_food(FOOD / fname, diam, rotate=rot)
            tray.paste(food, (cx - diam // 2, cy - diam // 2), food)
    return tray


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    before = make_tray(keep=False)
    after = make_tray(keep=True)
    before.save(OUT / "pair1_before.png")
    after.save(OUT / "pair1_after.png")
    gt = {f[1]: f[5] for f in FOODS}
    import json

    (OUT / "pair1_ground_truth.json").write_text(
        json.dumps(
            {
                "note": "After tabağındaki yemek alanı = keep_ratio x before alanı (sahnelenmiş).",
                "keep_ratios": gt,
            },
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )
    print(f"yazıldı: {OUT}/pair1_before.png, pair1_after.png")  # noqa: T201


if __name__ == "__main__":
    main()
