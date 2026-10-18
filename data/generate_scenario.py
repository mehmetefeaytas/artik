"""ARTIK senaryo (sentetik) veri üreteci — SABİT TOHUMLU, yeniden üretilebilir.

ÜRETİLEN HER ŞEY SENARYODUR: gerçek yemekhane ölçümü değildir.
Amaç: panelin ve öneri motorunun gerçekçi bir "baseline geçmişi" üzerinde
gösterilmesi. Gerçek veri geldiğinde data/real/ şemasıyla içe aktarılır.

Kullanım:  python data/generate_scenario.py
Çıktılar:  data/scenario/menu.json, measurements.json, feedback.json
"""

from __future__ import annotations

import json
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 42
START = date(2026, 8, 31)   # Pazartesi
END = date(2026, 10, 21)    # Perşembe
SITE = "pilot-universite"

# --- Menü kataloğu ----------------------------------------------------------
# base_waste: o yemeğin tipik (senaryo) yenilebilir tabak artığı oranı
ITEMS = {
    # çorbalar
    "mercimek_corbasi": ("Mercimek Çorbası", "red lentil soup", "corba", 250, 0.05),
    "ezogelin_corbasi": ("Ezogelin Çorbası", "ezogelin soup", "corba", 250, 0.06),
    "tarhana_corbasi": ("Tarhana Çorbası", "tarhana soup", "corba", 250, 0.07),
    "domates_corbasi": ("Domates Çorbası", "tomato soup", "corba", 250, 0.05),
    # ana yemekler
    "kuru_fasulye": ("Kuru Fasulye", "white bean stew", "ana", 280, 0.22),
    "nohut": ("Nohut Yemeği", "chickpea stew", "ana", 280, 0.20),
    "tavuk_sote": ("Tavuk Sote", "chicken sauté", "ana", 260, 0.12),
    "kofte": ("Köfte", "meatballs", "ana", 260, 0.08),
    "karniyarik": ("Karnıyarık", "stuffed eggplant", "ana", 280, 0.15),
    "etli_tencere": ("Etli Tencere Yemeği", "beef casserole", "ana", 280, 0.17),
    "mucver": ("Mücver", "zucchini fritters", "ana", 260, 0.28),
    "ispanak": ("Ispanak Yemeği", "spinach stew", "ana", 260, 0.26),
    "sebze_guvec": ("Sebze Güveç", "vegetable guvec", "ana", 280, 0.19),
    "tavuk_pirzola": ("Tavuk Pirzola", "chicken cutlet", "ana", 250, 0.10),
    "balik_izgara": ("Izgara Balık", "grilled fish", "ana", 250, 0.24),
    "mantar_sote": ("Mantar Sote", "mushroom sauté", "ana", 250, 0.18),
    # garnitür
    "pirinc_pilavi": ("Pirinç Pilavı", "rice pilaf", "garnitur", 180, 0.10),
    "bulgur_pilavi": ("Bulgur Pilavı", "bulgur pilaf", "garnitur", 180, 0.14),
    "makarna": ("Makarna", "pasta", "garnitur", 180, 0.09),
    "patates_kizartma": ("Patates Kızartma", "french fries", "garnitur", 180, 0.06),
    "sehriye_pilavi": ("Şehriye Pilavı", "orzo pilaf", "garnitur", 180, 0.12),
    # yan
    "coban_salata": ("Çoban Salata", "shepherd's salad", "yan", 150, 0.18),
    "yogurt": ("Yoğurt", "yogurt", "yan", 150, 0.07),
    "cacik": ("Cacık", "cacik (yogurt dip)", "yan", 150, 0.09),
    "tursu": ("Turşu", "pickles", "yan", 120, 0.12),
    "mevsim_salata": ("Mevsim Salata", "seasonal salad", "yan", 150, 0.16),
    # tatlı (bazı günler)
    "sup": ("Sütlaç", "rice pudding", "tatli", 120, 0.11),
    "komposto": ("Komposto", "compote", "tatli", 120, 0.13),
}

# 4 haftalık öğle rotasyonu: (çorba, ana, garnitür, yan, tatlı|None)
WEEK_ROTATION = [
    [
        ("mercimek_corbasi", "kuru_fasulye", "pirinc_pilavi", "coban_salata", None),
        ("ezogelin_corbasi", "tavuk_sote", "bulgur_pilavi", "yogurt", "sup"),
        ("tarhana_corbasi", "karniyarik", "makarna", "cacik", None),
        ("domates_corbasi", "kofte", "pirinc_pilavi", "mevsim_salata", None),
        ("mercimek_corbasi", "balik_izgara", "sehriye_pilavi", "coban_salata", None),
    ],
    [
        ("ezogelin_corbasi", "nohut", "pirinc_pilavi", "tursu", "komposto"),
        ("tarhana_corbasi", "tavuk_pirzola", "bulgur_pilavi", "yogurt", None),
        ("domates_corbasi", "etli_tencere", "makarna", "coban_salata", None),
        ("mercimek_corbasi", "ispanak", "sehriye_pilavi", "cacik", None),
        ("ezogelin_corbasi", "mantar_sote", "pirinc_pilavi", "mevsim_salata", None),
    ],
    [
        ("tarhana_corbasi", "kuru_fasulye", "bulgur_pilavi", "tursu", None),
        ("domates_corbasi", "mucver", "makarna", "yogurt", "sup"),
        ("mercimek_corbasi", "tavuk_sote", "sehriye_pilavi", "coban_salata", None),
        ("ezogelin_corbasi", "kofte", "pirinc_pilavi", "cacik", None),
        ("tarhana_corbasi", "balik_izgara", "bulgur_pilavi", "mevsim_salata", None),
    ],
    [
        ("domates_corbasi", "nohut", "makarna", "tursu", "komposto"),
        ("mercimek_corbasi", "sebze_guvec", "pirinc_pilavi", "yogurt", None),
        ("ezogelin_corbasi", "etli_tencere", "bulgur_pilavi", "coban_salata", None),
        ("tarhana_corbasi", "ispanak", "sehriye_pilavi", "cacik", None),
        ("domates_corbasi", "tavuk_pirzola", "makarna", "mevsim_salata", None),
    ],
]

# Hikaye öğeleri (senaryo içinde örnek senaryolar):
# 1) Sebze güveç yeni tarife geçiş: ilk gün artık fırlar, sonra oturur.
# 2) 6 Ekim: çorba soğuk servis olayı (tek günlük spike, neden: sicaklik).
# 3) Sınav haftası (12-16 Ekim): katılım düşer.
STORY_GUVEC_START = date(2026, 9, 22)  # rotasyona denk: week-3 salı (ilk güveç günü)
STORY_COLD_SOUP_DAY = date(2026, 10, 6)
EXAM_WEEK = (date(2026, 10, 12), date(2026, 10, 16))

FEEDBACK_RATE = 0.12  # artık bırakanlardan QR geri bildirimi veren pay (senaryo)


def base_meals(d: date, rng: random.Random) -> int:
    n = rng.gauss(880, 55)
    if d.weekday() == 4:
        n *= 0.85  # cuma
    if EXAM_WEEK[0] <= d <= EXAM_WEEK[1]:
        n *= 0.90
    return max(400, int(n))


def waste_for(key: str, d: date, rng: random.Random) -> float:
    base = ITEMS[key][4]
    # Beta benzeri gürültü: ortalama etrafında, [0, ~2x] aralığında
    w = rng.gauss(base, base * 0.25)
    if key == "sebze_guvec":
        if d == STORY_GUVEC_START:
            w = 0.34  # yeni tarife ilk gün tepkisi
        elif d <= STORY_GUVEC_START + timedelta(days=4):
            w += 0.05
    if key.endswith("_corbasi") and d == STORY_COLD_SOUP_DAY:
        w = max(w, base * 2.2)  # soğuk çorba olayı
    return max(0.01, min(0.55, w))


def reasons_for(w: float, key: str, d: date, rng: random.Random) -> dict[str, int]:
    if w > 0.20:
        weights = {"porsiyon_buyuk": 45, "tadi": 20, "cesit_tekrar": 14, "acele": 11, "sicaklik": 5, "diger": 5}
    elif w > 0.12:
        weights = {"tadi": 30, "porsiyon_buyuk": 28, "acele": 16, "cesit_tekrar": 14, "sicaklik": 7, "diger": 5}
    else:
        weights = {"acele": 35, "tadi": 15, "porsiyon_buyuk": 12, "cesit_tekrar": 10, "sicaklik": 10, "diger": 18}
    if key.endswith("_corbasi") and d == STORY_COLD_SOUP_DAY:
        weights = {"sicaklik": 70, "tadi": 10, "acele": 10, "diger": 10}
    total = sum(weights.values())
    return {k: v / total for k, v in weights.items()}


def main() -> None:
    rng = random.Random(SEED)
    out_dir = Path(__file__).parent / "scenario"
    out_dir.mkdir(parents=True, exist_ok=True)

    menu = {
        "meta": {"kind": "scenario", "seed": SEED, "site": SITE},
        "items": [
            {
                "key": k,
                "name_tr": v[0],
                "name_en": v[1],
                "category": v[2],
                "portion_g": v[3],
                "base_waste": v[4],
            }
            for k, v in ITEMS.items()
        ],
    }

    measurements = []
    feedback = []
    week_no = 0
    d = START
    while d <= END:
        if d.weekday() < 5:  # hafta içi
            day_menu = [k for k in WEEK_ROTATION[week_no % 4][d.weekday()] if k]
            meals = base_meals(d, rng)
            for key in day_menu:
                w = waste_for(key, d, rng)
                portion = ITEMS[key][3]
                leftover_g = meals * portion * w
                reasons = reasons_for(w, key, d, rng)
                top = max(reasons, key=reasons.get)
                measurements.append(
                    {
                        "date": d.isoformat(),
                        "meal": "ogle",
                        "site_id": SITE,
                        "item_key": key,
                        "item_name_tr": ITEMS[key][0],
                        "category": ITEMS[key][2],
                        "portion_g": portion,
                        "served_meals": meals,
                        "leftover_ratio": round(w, 4),
                        "edible_leftover_g": round(leftover_g, 1),
                        "reason_top": top,
                    }
                )
                n_fb = int(meals * w * FEEDBACK_RATE)
                for code, share in reasons.items():
                    cnt = rng.binomialvariate(n_fb, share) if hasattr(rng, "binomialvariate") else int(n_fb * share)
                    if cnt > 0:
                        feedback.append(
                            {
                                "date": d.isoformat(),
                                "meal": "ogle",
                                "item_key": key,
                                "reason_code": code,
                                "count": cnt,
                            }
                        )
            if d.weekday() == 4:
                week_no += 1
        d += timedelta(days=1)

    measurements_doc = {
        "meta": {
            "kind": "scenario",
            "seed": SEED,
            "site": SITE,
            "start": START.isoformat(),
            "end": END.isoformat(),
            "note": "SENARYO VERİSİDİR — gerçek yemekhane ölçümü değildir. "
            "Üretim: data/generate_scenario.py",
            "stories": [
                "sebze_guvec yeni tarife geçişi (2026-09-14 civarı spike)",
                "çorba soğuk servis olayı (2026-10-06, neden: sicaklik)",
                "sınav haftası katılım düşüşü (2026-10-12..16)",
            ],
        },
        "measurements": measurements,
    }

    (out_dir / "menu.json").write_text(
        json.dumps(menu, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    (out_dir / "measurements.json").write_text(
        json.dumps(measurements_doc, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    (out_dir / "feedback.json").write_text(
        json.dumps(feedback, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(f"menu: {len(menu['items'])} öğe")  # noqa: T201
    print(f"measurements: {len(measurements)} kayıt")  # noqa: T201
    print(f"feedback: {len(feedback)} kayıt")  # noqa: T201


if __name__ == "__main__":
    main()
