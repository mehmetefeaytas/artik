# ARTIK — Yemekhane Tabak Artığı Analiz ve Karar Destek Sistemi

> **ARTIK**: Yemekhane iade hattında kamera istasyonu ile yemek bazında tabak artığı tahmini,
> öğrenci geri bildirimiyle birleştirilmiş porsiyon ve menü karar desteği.
>
> English summary below.

**Status**: Prototip (Climathon 2026 — Siemens × YGA × UP School)

## Ne yapıyor?

1. **İstasyon**: Servis öncesi ve sonrası tepsi fotoğrafları (kamera veya yükleme)
2. **Analiz**: Zero-shot görü işleme (SAM segmentasyon + CLIP sınıflandırma) ile
   yemek bazında artık yüzdesi ve gram *tahmini* (ölçüm değil)
3. **Panel**: Zaman serisi, en çok artık bırakılan yemekler, neden kodları,
   CO₂e / su / maliyet etkisi, porsiyon önerileri
4. **Geri bildirim**: QR ile öğrenci "neden bıraktın?" seçimi

## Dürüstlük ilkeleri

- Görüntüden elde edilen gram değerleri **tahmindir**; tartım doğrulaması gerekir.
- Paneldeki 8 haftalık geçmiş **senaryo (sentetik) verisidir**, saha ölçümü değildir.
- Gerçek veri geldiğinde `data/real/` şemasıyla içe aktarılır ve arayüzde ayrı rozetle gösterilir.

## Depo yapısı

```
api/     FastAPI — görü işleme + istatistik uçları (Python 3.12, uv)
web/     Next.js 15 — istasyon, panel, geri bildirim, metodoloji sayfaları
data/    Senaryo üreteci + tohum veriler + gerçek veri şablonu
docs/    PDR, model kartı, kaynakça
demo/    Demo malzemeleri, fotoğraf rehberi, test görüntüleri
```

## Hızlı başlangıç

```bash
# API
cd api && uv sync && uv run uvicorn app.main:app --reload --port 8000

# Web
cd web && npm install && npm run dev
```

## Lisanslar ve atıflar

- Kod: MIT (bu depo)
- Modeller: SAM (Meta, MIT), CLIP (OpenAI, MIT) — HF transformers ile
- Saha doğrulama literatürü: UNIMIB2016 (Ciocca et al., IEEE JBHI 2017),
  FLIC (MDPI Applied Sciences, 2026) — bkz. `docs/`
- İstatistik çerçevesi: UNEP Food Waste Index 2024

---

## English

ARTIK is a prototype for institutional canteens: a tray-return station captures
before/after tray photos, a zero-shot vision pipeline (SAM + CLIP) estimates
per-dish edible leftovers, combines them with student reason-code feedback, and
turns the result into portion and menu decision support. All image-derived grams
are **estimates**; dashboard history is **clearly-labeled synthetic scenario data**
until real measurements are imported.
