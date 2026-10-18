# ARTIK — Yemekhane Tabak Artığı Analiz ve Karar Destek Sistemi

> **ARTIK**: Yemekhane iade hattında kamera istasyonu ile yemek bazında tabak
> artığı *tahmini*, öğrenci geri bildirimiyle birleştirilmiş porsiyon ve menü
> karar desteği.
>
> Climathon 2026 prototipi — Siemens × YGA × UP School.
> COP31 hedefi: Atığı 2035'e kadar yarıya indirmek · Siemens Etki Alanı:
> Kaynak Verimliliği ve Döngüsellik · SDG 12.3

## Ne yapıyor?

1. **İstasyon** (`/istasyon`) — Günün menüsü seçilir; servis öncesi ve sonrası
   tepsi fotoğrafları (kamera veya yükleme) analiz edilir
2. **Analiz** — Zero-shot görü işleme (SAM segmentasyonu + CLIP sınıflandırması):
   yemek bazında artık yüzdesi ve gram **tahmini** (eğitim yok, her menüye uyarlanır)
3. **Panel** (`/panel`) — Zaman serisi, en çok artık bırakılan yemekler, neden
   kodları, CO₂e / su / maliyet etkisi, porsiyon önerileri ve simülasyon
4. **Geri bildirim** (`/geri-bildirim`) — QR ile tek dokunuş "neden bıraktın?"
5. **Yöntem** (`/yontem`) — Dürüstlük beyanı: ne ölçülüyor, ne varsayılıyor

## Dürüstlük ilkeleri (ürünün parçasıdır)

- Görüntüden elde edilen gram değerleri **tahmindir**; tartım doğrulaması gerekir →
  arayüzde kalıcı `TAHMİN` damgası
- Paneldeki 8 haftalık geçmiş **senaryo (sentetik) verisidir** → `SENARYO` damgası;
  sabit tohumla yeniden üretilebilir (`data/generate_scenario.py`)
- Gerçek istasyon kayıtları panelde **ayrı bölümde** gösterilir
- Etki simülasyonları aralık raporlar (muhafazakâr → iyimser model) → `SİMÜLASYON` damgası

## Mimari

```
┌────────────────────────────┐        ┌──────────────────────────────────────┐
│ web/  Next.js 16 (Pages)   │        │ api/  FastAPI                        │
│                            │        │                                      │
│  /istasyon ──analyze──────▶│───────▶│  SAM ViT-B (MIT)       segmentasyon  │
│  /panel    ◀──stats────────│        │  CLIP ViT-B/32 (MIT)   sınıflandırma │
│  /geri-bildirim ─feedback─▶│        │  EVREN VLM (qwen3-vl)  arabuluculuk  │
│  /yontem                   │        │  SQLite                vizyon kayıt │
└────────────────────────────┘        │  senaryo tohumu        data/scenario│
                                      └──────────────────────────────────────┘
```

- **Zero-shot tercih sebebi**: Menü etiketleri istekle geçtiği için model
  eğitimi gerekmez ve her yemekhane menüsüne uyarlanır.
- **Hibrit sınıflandırma**: CLIP ilk geçiş; belirsiz maskelerde (tabak+yemek
  birleşik vb.) Türkiye'nin ulusal LLM altyapısı EVREN'deki görsel modele
  (qwen3-vl-30b, Apache-2.0) tek çağrıyla sorulur. EVREN erişilemezse pipeline
  saf CLIP ile çalışmaya devam eder.
- **Lisans temizliği**: AGPL'li Ultralytics bilinçli olarak kullanılmadı.
- **Gerçek veri setiyle doğrulama**: UNIMIB/Padova üniversite yemekhanesi
  tepsileri (8 tepsi × 24 önce/sonra çifti, ground-truth maskeli) —
  `demo/real_dataset` + `api/scripts/validate_real.py`. Sonuçlar model kartında.

## Hızlı başlangıç (yerel)

```bash
# API (port 8000)
cd api && uv sync && uv run uvicorn app.main:app --reload

# Web (port 3000)
cd web && npm install && npm run dev
```

İlk API çalıştırması SAM checkpoint'ini (~375 MB) ve CLIP'i indirir.
Analiz yerel Mac'te ~30–60 sn sürer (2 görüntü).

## Demo akışı (2 dakikalık senaryo)

1. `/istasyon` → "Hızlı demo menüsü" + "Demo çiftini kullan" → "Analizi çalıştır"
2. Sonuç kartları: % yenildi / % kaldı / tahmini gram
3. `/panel` → ıspanak-balık-fasulye hikayesi, öneriler, simülasyon
4. `/geri-bildirim` → tek dokunuş neden kodu
5. `/yontem` → jüri sorularına hazır dürüstlük çerçevesi

Gerçek çekimli demo için: `demo/PHOTO_GUIDE.md` (4–5 önce/sonra tepsi çifti).

## Test ve doğrulama

```bash
cd api
uv run python ../data/generate_scenario.py   # senaryoyu yeniden üret
uv run python scripts/test_pipeline.py       # kompozit çiftte uçtan uca test
uv run python scripts/diagnose.py            # maske/CLIP teşhisi
uv run ruff check .                          # lint
```

Kompozit test sonucu: ortalama mutlak hata ≈ 0,08 (bkz. `docs/MODEL_CARD.md`).

## Depo yapısı

```
api/     FastAPI — görü işleme + istatistik uçları (Python 3.12, uv)
web/     Next.js 16 — istasyon, panel, geri bildirim, yöntem (TR/EN)
data/    Senaryo üreteci + tohumlar + gerçek veri şablonu
docs/    PDR, model kartı, deploy kılavuzu
demo/    Fotoğraf rehberi, test çiftleri, kaynak fotoğraflar
```

## Deploy

- Web → Vercel (Root: `web`, env: `NEXT_PUBLIC_API_URL`)
- API → Hugging Face Space (Docker, ücretsiz CPU)
- Ayrıntılı adımlar: `docs/DEPLOY.md`
- API erişilemezse istasyon otomatik demo moduna düşer

## Lisanslar ve atıflar

- Kod: **MIT** (bu depo)
- Modeller: SAM (Meta, MIT), CLIP (OpenAI, MIT) — HF transformers üzerinden
- Doğrulama literatürü: UNIMIB2016 (Ciocca ve diğ., IEEE JBHI 2017);
  FLIC (MDPI Applied Sciences, 2026)
- İstatistik çerçevesi: UNEP Food Waste Index 2024
- Test fotoğrafları: Wikimedia Commons (CC BY-SA) — `demo/sample_food/CREDITS.md`

## English summary

ARTIK is a prototype for institutional canteens: a tray-return station captures
before/after tray photos, a zero-shot vision pipeline (SAM + CLIP, both MIT
licensed) estimates per-dish edible leftovers, student QR feedback adds reasons,
and a dashboard turns the signal into portion and menu decisions. All
image-derived grams carry an **ESTIMATE** stamp; dashboard history is
**clearly-labeled synthetic scenario data**; real records display separately.
Method, limitations and validation are documented in `docs/`.
