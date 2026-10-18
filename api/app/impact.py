"""Etki dönüşüm katsayıları — her sayı kaynak etiketlidir ve varsayımdır.

Değerler kurum/yöre bazında kalibre edilmelidir; buradaki sayılar prototip
demosu için makul küresel ortalamalardır.
"""

CO2E_KG_PER_KG_FOOD = 2.5
# Kaynak yaklaşımı: UNEP Food Waste Index 2024 / FUSIONS — gıda atığı yaşam döngüsü
# emisyonu için yaygın kullanılan ~2.5 kgCO2e/kg bileşik katsayı (yaklaşık).

WATER_L_PER_KG_FOOD = 1500.0
# Kaynak yaklaşımı: Mekonnen & Hoekstra (2011) gıda su ayak izi ortalamalarından
# kaba yaklaşım (tahıl/sebze/et karışımı); kurum bazında kalibre edilmeli.

COST_TL_PER_KG_FOOD = 95.0
# Varsayım: yemekhane girdi maliyeti ~95 TL/kg (2026, ayarlanabilir parametre).

REASONS_TR = {
    "porsiyon_buyuk": "Porsiyon büyüktü",
    "tadi": "Tadını beğenmedim",
    "sicaklik": "Soğuk servis edildi",
    "cesit_tekrar": "Sık tekrarlanıyor",
    "acele": "Vaktim yoktu / acelem vardı",
    "diger": "Diğer",
}

REASONS_EN = {
    "porsiyon_buyuk": "Portion was too big",
    "tadi": "Didn't like the taste",
    "sicaklik": "Served cold",
    "cesit_tekrar": "Too repetitive",
    "acele": "Was in a hurry",
    "diger": "Other",
}


def impact_from_kg(kg: float) -> dict:
    return {
        "kg": round(kg, 2),
        "co2e_kg": round(kg * CO2E_KG_PER_KG_FOOD, 1),
        "water_l": round(kg * WATER_L_PER_KG_FOOD),
        "cost_tl": round(kg * COST_TL_PER_KG_FOOD),
    }
