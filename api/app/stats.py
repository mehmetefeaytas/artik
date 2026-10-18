"""Panel agregasyonu: senaryo + gerçek veri birleştirme, öneriler, simülasyon.

Dürüstlük kuralı: senaryo verisi ve gerçek (vizyon/tartım) kayıtları ayrı
bölümlerde döner; asla tek seride karıştırılmaz.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta

from . import impact as impact_mod
from . import scenario

SIM_HORIZON_DAYS = 180  # bir akademik yıl yaklaşımı
REC_WINDOW_DAYS = 21
MIN_APPEARANCES = 3


def _recent(records: list[dict], days: int) -> list[dict]:
    if not records:
        return []
    last = max(r["date"] for r in records)
    cutoff = (datetime.fromisoformat(last) - timedelta(days=days)).date().isoformat()
    return [r for r in records if r["date"] >= cutoff]


def _daily_series(records: list[dict]) -> list[dict]:
    by_day: dict[str, dict] = {}
    for r in records:
        d = by_day.setdefault(
            r["date"], {"date": r["date"], "meal": r["meal"], "meals": r["served_meals"], "g": 0.0}
        )
        d["g"] += r["edible_leftover_g"]
    out = []
    for d in sorted(by_day.values(), key=lambda x: x["date"]):
        out.append(
            {
                "date": d["date"],
                "meal": d["meal"],
                "meals": d["meals"],
                "leftover_kg": round(d["g"] / 1000, 1),
                "g_per_meal": round(d["g"] / max(d["meals"], 1), 1),
            }
        )
    return out


def _item_stats(records: list[dict], window: list[dict]) -> list[dict]:
    per: dict[str, list[dict]] = defaultdict(list)
    for r in window:
        per[r["item_key"]].append(r)
    n_days = len({r["date"] for r in window}) or 1
    fb = _feedback_by_item()
    out = []
    for key, rows in per.items():
        if len(rows) < MIN_APPEARANCES:
            continue
        ratios = [r["leftover_ratio"] for r in rows]
        avg_w = sum(ratios) / len(ratios)
        total_kg = sum(r["edible_leftover_g"] for r in rows) / 1000
        daily_meals = sum(r["served_meals"] for r in rows) / len(rows)

        recent7 = [r["leftover_ratio"] for r in rows if r["date"] >= _shift(rows, 7)]
        prior = [r["leftover_ratio"] for r in rows if r["date"] < _shift(rows, 7)]
        trend = "flat"
        if recent7 and prior:
            ra, pa = sum(recent7) / len(recent7), sum(prior) / len(prior)
            trend = "up" if ra > pa * 1.15 else ("down" if ra < pa * 0.85 else "flat")

        reasons = fb.get(key, {})
        top_reason = max(reasons, key=reasons.get) if reasons else None

        out.append(
            {
                "key": key,
                "name_tr": rows[0]["item_name_tr"],
                "category": rows[0].get("category", ""),
                "portion_g": rows[0].get("portion_g"),
                "appearances": len(rows),
                "serving_freq": round(len(rows) / n_days, 3),
                "avg_daily_meals": round(daily_meals),
                "avg_leftover_pct": round(avg_w * 100, 1),
                "total_kg": round(total_kg, 1),
                "trend": trend,
                "top_reason": top_reason,
                "reasons": reasons,
            }
        )
    return sorted(out, key=lambda x: -x["avg_leftover_pct"])


def _shift(rows: list[dict], days: int) -> str:
    last = max(r["date"] for r in rows)
    return (datetime.fromisoformat(last) - timedelta(days=days)).date().isoformat()


def _feedback_by_item() -> dict[str, dict[str, int]]:
    per: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for f in scenario.feedback():
        per[f["item_key"]][f["reason_code"]] += f["count"]
    return per


def _reason_distribution() -> list[dict]:
    totals: dict[str, int] = defaultdict(int)
    for f in scenario.feedback():
        totals[f["reason_code"]] += f["count"]
    total = sum(totals.values()) or 1
    return sorted(
        [
            {
                "code": code,
                "name_tr": impact_mod.REASONS_TR.get(code, code),
                "name_en": impact_mod.REASONS_EN.get(code, code),
                "count": n,
                "share": round(n / total, 3),
            }
            for code, n in totals.items()
        ],
        key=lambda x: -x["count"],
    )


def _simulate_portion(item: dict) -> dict:
    w = item["avg_leftover_pct"] / 100
    r = min(0.6 * w, 0.25)
    p = item["portion_g"] or 250
    reasons = item.get("reasons") or {}
    fb_total = sum(reasons.values()) or 1
    porsiyon_share = min(max(reasons.get("porsiyon_buyuk", 0) / fb_total, 0.3), 1.0)

    new_p = round(p * (1 - r))
    red_g = p - new_p
    meals = item["avg_daily_meals"]
    # Yemek her gün servis edilmez: penceredeki servis sıklığıyla ölçekle
    servings = meals * (item.get("serving_freq") or 1.0) * SIM_HORIZON_DAYS

    low_g = red_g * porsiyon_share
    high_g = red_g
    kg_low = servings * low_g / 1000
    kg_high = servings * high_g / 1000
    return {
        "reduction_pct": round(r * 100),
        "old_portion_g": p,
        "new_portion_g": new_p,
        "porsiyon_share": round(porsiyon_share, 2),
        "model": "aralık: muhafazakâr (neden kodu payıyla) → iyimser (tam porsiyon etkisi)",
        "saved_g_per_meal_low": round(low_g, 1),
        "saved_g_per_meal_high": round(high_g, 1),
        "horizon_days": SIM_HORIZON_DAYS,
        "saved_kg_low": round(kg_low),
        "saved_kg_high": round(kg_high),
        "impact_low": impact_mod.impact_from_kg(kg_low),
        "impact_high": impact_mod.impact_from_kg(kg_high),
    }


def _recommendations(items: list[dict]) -> list[dict]:
    recs = []
    for it in items:
        w = it["avg_leftover_pct"]
        top = it.get("top_reason")
        if w >= 20:
            rec_type = "portion"
            text_tr = (
                f"{it['name_tr']} son {REC_WINDOW_DAYS} günde ortalama %{w:.0f} artık bırakılıyor. "
                f"Porsiyonu azaltmayı veya yarım porsiyon seçeneğini pilotlamayı öner."
            )
            text_en = (
                f"{it['name_tr']} averages {w:.0f}% leftovers. Pilot a portion reduction "
                f"or a half-portion option."
            )
            priority = "high"
        elif w >= 12:
            rec_type = "watch"
            text_tr = (
                f"{it['name_tr']} ortalama %{w:.0f} artık — izlemede tut, "
                "yarım porsiyon pilotu için aday."
            )
            text_en = (
                f"{it['name_tr']} averages {w:.0f}% leftovers — "
                "keep watching; half-portion candidate."
            )
            priority = "medium"
        else:
            continue
        if top == "tadi" and w >= 12 and rec_type == "watch":
            rec_type = "kitchen"
            text_tr += (
                " Baskın neden 'tadı beğenmedim' — mutfak ekibine tarif/"
                "servis geri bildirimi ilet."
            )
            text_en += " Top reason is taste — pass feedback to the kitchen team."
        recs.append(
            {
                "item_key": it["key"],
                "name_tr": it["name_tr"],
                "avg_leftover_pct": w,
                "top_reason": top,
                "type": rec_type,
                "priority": priority,
                "text_tr": text_tr,
                "text_en": text_en,
                "simulation": _simulate_portion(it) if rec_type == "portion" else None,
            }
        )
    return sorted(recs, key=lambda r: -(r["avg_leftover_pct"] or 0))


def _real_section(store) -> dict:
    rows = store.measurements()
    by_item: dict[str, dict] = {}
    for r in rows:
        d = by_item.setdefault(
            r["item_key"],
            {"key": r["item_key"], "name_tr": r["item_name_tr"], "trays": 0, "total_g": 0.0},
        )
        d["trays"] += 1
        d["total_g"] += r["estimated_leftover_g"]
    items = [
        {
            **d,
            "total_g": round(d["total_g"], 1),
            "avg_g_per_tray": round(d["total_g"] / d["trays"], 1),
        }
        for d in by_item.values()
    ]
    total_kg = sum(i["total_g"] for i in items) / 1000
    return {
        "trays_analyzed": len(rows),
        "total_kg": round(total_kg, 2),
        "impact": impact_mod.impact_from_kg(total_kg),
        "by_item": sorted(items, key=lambda x: -x["total_g"]),
        "recent": rows[-20:],
        "note": "Görüntüden tahmin edilen tekil tepsi kayıtları (tartım doğrulaması yok).",
    }


def build_stats(store, days: int = 56) -> dict:
    all_rec = scenario.measurements()
    records = _recent(all_rec, days)
    series = _daily_series(records)
    items = _item_stats(all_rec, records)

    meals = sum(d["meals"] for d in series)
    total_kg = sum(d["leftover_kg"] for d in series)
    g_per_meal = (total_kg * 1000 / meals) if meals else 0
    avg_w = sum(i["avg_leftover_pct"] * i["appearances"] for i in items) / max(
        sum(i["appearances"] for i in items), 1
    )

    return {
        "meta": {
            "kind": "scenario+real",
            "scenario_note": "Panel geçmişi senaryo (sentetik) verisidir; saha ölçümü değildir.",
            "days": days,
            "scenario_records": len(records),
            "scenario_meta": scenario.scenario_meta(),
            "generated_at": datetime.now().isoformat(timespec="seconds"),
        },
        "summary": {
            "meals_served": meals,
            "total_leftover_kg": round(total_kg, 1),
            "g_per_meal": round(g_per_meal, 1),
            "avg_leftover_pct": round(avg_w, 1),
            "impact": impact_mod.impact_from_kg(total_kg),
        },
        "daily": series,
        "items": items,
        "reasons": _reason_distribution(),
        "recommendations": _recommendations(items),
        "real": _real_section(store),
    }
