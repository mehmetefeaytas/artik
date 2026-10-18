# ARTIK Model Kartı

**Sürüm**: 0.1 (prototip) · **Tarih**: 18 Ekim 2026

## Özet

ARTIK görü işleme hattı, yemekhane tepsisinin servis öncesi ve sonrası
fotoğraflarından yemek bazında yenilebilir artık **oranı** tahmin eder.
Üç açık kaynak/ulusal bileşenin zero-shot zinciridir:

| Aşama | Bileşen | Görev | Lisans |
|---|---|---|---|
| Segmentasyon | SAM ViT-B (`sam_vit_b_01ec64`) | Tepsideki nesne maskeleri | MIT (Meta) |
| Sınıflandırma (1. geçiş) | CLIP ViT-B/32 (`openai/clip-vit-base-patch32`) | Maskeyi günün menü etiketleriyle eşleme | MIT (OpenAI) |
| Arabuluculuk (2. geçiş) | EVREN VLM (`qwen3-vl-30b`) — Türkiye ulusal LLM altyapısı | CLIP'in belirsiz kaldığı maskelerde görsel karar | Apache-2.0 (Qwen) |

**Eğitim yok** (zero-shot). Menü etiketleri her istekte API'ye geçer; bu yüzden
sistem belirli bir yemek setine bağlı değildir. CLIP'e her yemek için görsel
açıdan açıklayıcı İngilizce prompt verilir (ör. kuru fasulye → "a plate of
stewed white beans, individual beans visible in red sauce").

**Hibrit karar mantığı**: Her maske için CLIP olasılıkları hesaplanır.
(1) Menü etiketi açık ara kazanırsa kabul, (2) menü dışı aday açık ara
kazanırsa red, (3) **belirsiz bölgedeyse** (ör. "tabak+yemek birleşik kaba
maskede" CLIP'in 'boş tabak' yanıtı yemekle yarışırsa) EVREN VLM'e tek çağrıda
toplu sorulur; VLM yanıtı menü etiketiyle eşleşirse kabul edilir. EVREN
erişilemezse pipeline saf CLIP ile çalışmaya devam eder (offline demo güvencesi).

## Girdi / çıktı

- **Girdi**: (a) önce/sonra iki RGB görüntü (uzun kenar 768 px'e ölçeklenir),
  (b) menü: anahtar, TR/EN ad, CLIP prompt, porsiyon gram.
- **Çıktı**: Öğe başına artık oranı = alan(sonra)/alan(önce); tahmini gram =
  oran × porsiyon; güven skoru; açıklamalı overlay görüntüleri.

## Kabul eşikleri

- Maske alanı görüntünün %0,4–45'ü arasında
- CLIP olasılığı > 0,25 ve en yakın "menü dışı" adaydan (boş tabak, çatal,
  tepsi…) en az 0,05 fazla (CLIP'in öğrenilmiş logit ölçeğiyle)
- Aynı etiketli örtüşen maskeler IoU>0,5 veya kapsama>0,6 ile elenir; ayrık
  parçaların alanları toplanır
- Oran > 1,2 → uyarı üretilir ve 1,0'a sabitlenir

## Doğrulama

### 1) Kontrollü (sahnelenmiş kompozit) test

Wikimedia Commons'tan CC lisanslı gerçek yemek fotoğraflarından, bilinen artık
oranlarıyla üretilmiş önce/sonra tepsileri (`demo/make_pair.py`):

| Yemek | Gerçek oran | Tahmin | Hata |
|---|---|---|---|
| Mercimek çorbası | 0,05 | 0,000 | 0,05 |
| Kuru fasulye | 0,62 | 0,623 | 0,003 |
| Pirinç pilavı | 0,15 | 0,114 | 0,036 |
| Çoban salata | 0,85 | 0,631 | 0,219 |

Ortalama mutlak hata ≈ 0,08 (mekanik doğrulama; saha ölçümü değildir).

### 2) Gerçek saha verisi testi (UNIMIB/Padova tepsileri)

`demo/real_dataset`: gerçek üniversite yemekhanesinde çekilmiş 8 tepsi ×
(servis + 3 artık durumu) = 24 çift, **piksel hassasiyetinde ground-truth
yemek maskeleriyle**. Doğrulama: `api/scripts/validate_real.py`
(gerçek oran = maskelerden alan oranı; tahmin = ARTIK pipeline çıktısı).

**Sonuçlar** (`demo/real_dataset/val_results.json` — çalıştırıldığında güncellenir):

- Tespit oranı, eşleşen öğelerde ortalama mutlak hata ve tepsi bazında kırılım
  script çıktısında raporlanır.
- Bilinen kırılım noktaları (aşağıda) bu veri setinde gözlemlenmiştir: bitişik
  tabakların tek SAM maskesinde birleşmesi, çift-çekim arası ışık/açı değişimi,
  yarım yenmiş tabaklarda 'boş tabak' karışıklığı (VLM arabuluculuğu bunu
  kısmen azaltır).

Bu, saha/tartım doğrulaması değildir; gerçek fotoğraflarda dayanıklılık ölçümüdür.

## Bilinen başarısız modları

1. **Bitişik tabakların birleşmesi** (gerçek veri setinde gözlemlendi): SAM,
   yan yana duran iki tabağı tek maskede birleştirebilir — alan tek yemeğe
   yazılır, diğeri kaçar. Çözüm yolu (v2): tabak tespiti + maske bölme.
2. **Karışık dokulu yemekler** (çoban salata): SAM maskeleri parçalayabilir →
   oran düşük okunur (muhafazakâr yön; israfı az göstermez, fazla göstermez).
3. **Benzer görünümlü yemekler** (çorba ↔ kuru fasulye): CLIP karıştırabilir →
   prompt mühendisliğiyle büyük ölçüde azaltıldı; tam çözülmedi.
4. **Yarım yenmiş tabakta 'boş tabak' karışıklığı** (gerçek veri setinde
   gözlemlendi): Tabak halkası baskın kaba maskelerde CLIP 'boş tabak' der;
   VLM arabuluculuğu bu vakaların bir kısmını kurtarır.
5. **Açı/değişen kadraj**: Önce/sonra çekim açısı farklıysa oran sapar →
   uyarı mekanizması + fotoğraf rehberi (`demo/PHOTO_GUIDE.md`).
6. **Çekimler arası yer değişimi**: Tabaklar hareket ederse konum tabanlı
   eşleme bozulur — ARTIK etiket tabanlı eşler, bu sorunu tasarımıyla çözer
   (UNIMIB veri setinde teyit edildi).
7. **Çok küçük artıklar** (< görüntünün %0,4'ü): ölçülmez.

## Etik ve gizlilik

- Yüz veya kişi verisi işlenmez; yalnız tepsi görüntüsü analiz edilir.
- Öğrenci geri bildirimi anonimdir (neden kodu + opsiyonel yemek).
- Çıktılar arayüzde kalıcı **TAHMİN** damgası taşır; tartım doğrulaması
  olmadan ölçüm gibi sunulmaz.

## Gerçek saha doğrulaması planı

Pilot yemekhanede örneklem günlerinde tartımlı baseline; tahmin-tartım
düzeltme katsayısı (kalibrasyon eğrisi) çıkarılacak; `measurement_method`
alanıyla tahmin/tartım kayıtları ayrı tutulacaktır.
