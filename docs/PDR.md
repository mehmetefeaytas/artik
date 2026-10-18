# ARTIK — Ürün Tasarım Dokümanı (PDR)

**Climathon 2026 · Siemens × YGA × UP School**
Sürüm 0.1 · 18 Ekim 2026 · Durum: Prototip (MVP)

---

## 1. Problem

Üniversite ve kurum yemekhanelerinde standart menü ve sabit porsiyonlar,
öğrencilerin tüketim tercihleriyle örtüşmediğinde yenilebilir yemek tabakta
kalıyor. Yemek ve porsiyon kararları gerçek tüketim geri bildirimiyle
güncellenmediği için bu israf sistemsel olarak tekrarlanıyor.

**Kanıt ve mevcut durum (baseline):**
- Gümüşhane Üniversitesi yemekhane araştırması (2023, n=330): öğrencilerin
  %80,3'ü tabakta artık bıraktığını bildiriyor; nedenler: soğuk servis, tat,
  görünüm, tekrar.
- UNEP Food Waste Index 2024: gıda hizmetleri sektöründe 2022'de ~290 milyon
  ton gıda atığı.
- Yerel baseline ölçütü (pilotte kullanılacak): **gram yenilebilir tabak
  artığı / servis edilen öğün**, yemek türü bazında.

## 2. Kök neden analizi

Codex destekli araştırma (3 Ekim 2026) iki aday problem ayırt etti: (a) tabak
artığı, (b) servis edilmemiş üretim fazlası. Bu prototip **(a) tabak artığına**
odaklanır; çünkü iade hattındaki ölçüm, öğrenci geri bildirimiyle birleşerek
hem porsiyon hem menü kararlarını besleyen en doğrudan sinyaldir.

Kök neden adayları (hipotez; pilotte sınanacak):
- Sabit porsiyon + istenmeyen yemeği almak zorunda olmak
- Servis sıcaklığı / tat / tekrar kaynaklı tüketim reddi
- Artık verisinin ölçülmemesi → kararların sezgiye dayanması

## 3. Çözüm konsepti

**ARTIK**, iade hattında kamera istasyonu + karar destek paneli + öğrenci QR
geri bildiriminden oluşan üç yüzeyli bir sistemdir:

1. **İstasyon** — Servis öncesi ve sonrası tepsi fotoğrafları; zero-shot görüntü
   işleme (SAM + CLIP) ile yemek bazında artık oranı ve gram **tahmini**.
2. **Panel** — Yemek bazında artık trendi, neden kodları, CO₂e/su/maliyet
   etkisi, kural tabanlı porsiyon önerileri ve etki simülasyonu.
3. **Geri bildirim** — İade sırasında tek dokunuşla "neden bıraktın?" (QR).

**Dürüstlük ilkesi**: Görüntüden gram = tahmin (tartım doğrulaması gerekir);
paneldeki geçmiş = açıkça etiketlenmiş senaryo verisi; gerçek kayıtlar ayrı
bölümde. Bu ayrım arayüzde kalıcı damgalarla görünür.

## 4. Kullanıcılar

| Kullanıcı | İhtiyaç | ARTIK'tan aldığı |
|---|---|---|
| Yemekhane işletmecisi | Maliyet ve israf kontrolü | kg/öğün, maliyet, porsiyon önerileri |
| Menü planlayıcısı/aşçı | Hangi yemek neden kalıyor | Yemek bazlı artık + neden kodları |
| Öğrenci | Lezzetli, yeterli, uygun fiyatlı öğün | Sürdürülebilir hizmet; QR ile ses |
| Üniversite yönetimi | Sürdürülebilirlik raporlaması | CO₂e/su eşdeğeri, SDG 12.3 hattı |

## 5. Gereksinimler

### MVP (bu prototip)
- F1: Menü seçimli önce/sonra tepsi analizi (kamera veya yükleme)
- F2: Yemek bazlı artık oranı + gram tahmini + güven skoru
- F3: Sonucun panele kaydı (vizyon kaynağı etiketiyle)
- F4: Panel: özet, trend, yemek sıralaması, neden dağılımı
- F5: Kural tabanlı öneriler + porsiyon simülasyonu (aralık raporlu)
- F6: QR geri bildirim (6 neden kodu)
- F7: Yöntem sayfası: ölçülen/tahmin ayrımı, sınırlamalar, kaynaklar
- F8: TR/EN arayüz
- NF1: API koptuğunda demo modu (ön-hesaplanmış sonuç)
- NF2: Yüz/kişi verisi işlenmez; yalnız tepsi görüntüsü

### v2 backlog (hackathon sonrası)
- Tartım doğrulaması ile kalibrasyon (measurement_method=tartim)
- Gerçek katılım verisiyle üretim fazlası/talep modülü
- Yarım porsiyon tercih sisteminin POS entegrasyonu
- Toplam tartım cihazından otomatik CSV içe aktarma

## 6. Mimari ve teknoloji seçimleri

```
web (Next.js 16, Vercel)          api (FastAPI, HF Space)
 ├─ /istasyon  ── analiz ────────▶ ├─ SAM ViT-B segmentasyon
 ├─ /panel     ◀─ /stats ─────────┤ ├─ CLIP ViT-B/32 zero-shot
 ├─ /geri-bildirim ── /feedback ─▶ ├─ SQLite (vizyon kayıtları)
 └─ /yontem                        └─ senaryo tohumu (data/scenario)
```

- **Zero-shot (SAM+CLIP), eğitim yok**: Menü etiketleri istekle geçildiği için
  her yemekhane menüsüne uyarlanır; hackathon süresinde model eğitimi riski
  yok. Alternatif (fine-tune UNIMIB2016) değerlendirildi: İtalyan yemeklerine
  özgü kalır, Türk menüsünde zayıf kalırdı. UNIMIB2016 doğrulama literatürü
  olarak atıf taşıyor.
- **Lisans temizliği**: Ultralytics (AGPL) bilinçli olarak kullanılmadı;
  SAM (MIT) + CLIP (MIT) transformers üzerinden.
- **Senaryo verisi**: Sabit tohumlu, yeniden üretilebilir
  (`data/generate_scenario.py`); hikaye öğeleri (yeni tarif tepkisi, soğuk çorba
  olayı, sınav haftası) panelin anlatısını test eder.

## 7. Ölçüm ve etki planı

1. **Baseline (0–2 hafta)**: Pilot yemekhanede istasyonla (veya tartımla)
   g/öğün ölçümü, yemek bazında.
2. **Müdahale (2–6 hafta)**: En yüksek artıklı 2–3 yemekte porsiyon azaltma
   veya yarım porsiyon seçeneği; menü değişikliği mutfak ekibiyle.
3. **Karşılaştırma**: Benzer menü/katılım günlerinde baseline'a göre değişim;
   mümkünse paralel bir kontrol hattı.
4. **Guardrail metrikleri**: Yemek bulunamama oranı, memnuniyet anketi,
   porsiyon yeterlilik şikayetleri. "Öğrenciyi aç bırakan optimizasyon"
   başarılı sayılmaz.

Etki dönüşümleri (kalibre edilebilir varsayımlar): 2,5 kgCO₂e/kg (UNEP FWI
2024 bileşiği), ~1500 L su/kg (Mekonnen & Hoekstra 2011 yaklaşımı),
95 TL/kg girdi maliyeti.

## 8. AI gerekliliği ve sınırlamalar

**Neden AI**: Yüzlerce tepsi/gün akışında insan etiketlemesi sürdürülemez;
görsel sınıflandırma + alan karşılaştırma, tartı olmadan sürekli ve ölçeklenebilir
bir tahmin sinyali üretir. Basit kurallar (maske eşiği, uyarılar) deterministik
kısmı taşır.

**Sınırlamalar** (model kartında detay): Karışık salatalarda segmentasyon
parçalanabilir (tahmin muhafazakâr kalır); benzer görünümlü yemekler (çorba /
kuru fasulye) CLIP'te karışabilir (prompt mühendisliğiyle azaltıldı); kamera
açısı değişimi oran sapması üretir (oran > 1,2 uyarıya dönüşür).

## 9. Riskler

| Risk | Azaltım |
|---|---|
| Tahminler gerçekten tartımdan sapar | Pilotte örneklem tartım doğrulaması; TAHMİN damgası |
| Öğrenci kabulü (kamera algısı) | Yüz yok; yalnız tepsi; KVKK notu yöntem sayfasında |
| İşletme "az üret" baskısı | Guardrail metrikleri + menü kalite sinyali aynı panelde |
| Demo sırasında API arızası | Yerel çalıştırma + demo modu + kayıtlı video |

## 10. Yol haritası

- **Kasım 2026 (COP31)**: Prototip demo; pilot görüşmeleri (erişim: sürdürülebilirlik
  hocası, belediye başkan yardımcısı, endüstri mühendisi).
- **Aralık 2026 – Şubat 2027**: Bir üniversite yemekhanesinde baseline pilotu;
  tartım doğrulaması; ölçülmüş etki raporu.
- **2027**: Yarım porsiyon POS entegrasyonu; üretim fazlası modülü; çoklu kurum.

## 11. Kaynakça

- Ciocca, Napoletano, Schettini (2017). *Food recognition: a new dataset,
  experiments and results.* IEEE JBHI. (UNIMIB2016)
- FLIC dataset (2026). *Visual Estimation of Food Leftovers in Canteens.*
  MDPI Applied Sciences 16(11):5465.
- UNEP (2024). *Food Waste Index Report 2024.*
- Gümüşhane Üniversitesi yemekhane araştırması (2023) — tabak artığı davranışı.
- SLU (2022). İsveç okul yemekhanelerinde talep tahmini deneyi — müdahale
  literatür desteği.
