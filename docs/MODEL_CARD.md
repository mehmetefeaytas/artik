# ARTIK Model Kartı

**Sürüm**: 0.1 (prototip) · **Tarih**: 18 Ekim 2026

## Özet

ARTIK görü işleme hattı, yemekhane tepsisinin servis öncesi ve sonrası
fotoğraflarından yemek bazında yenilebilir artık **oranı** tahmin eder.
Tek bir model değil, iki açık kaynak modelin zero-shot zinciridir:

| Aşama | Model | Görev | Lisans |
|---|---|---|---|
| Segmentasyon | SAM ViT-B (`sam_vit_b_01ec64`) | Tepsideki nesne maskeleri | MIT (Meta) |
| Sınıflandırma | CLIP ViT-B/32 (`openai/clip-vit-base-patch32`) | Maskeyi günün menü etiketleriyle eşleme | MIT (OpenAI) |

**Eğitim yok** (zero-shot). Menü etiketleri her istekte API'ye geçer; bu yüzden
sistem belirli bir yemek setine bağlı değildir. CLIP'e her yemek için görsel
açıdan açıklayıcı İngilizce prompt verilir (ör. kuru fasulye → "a plate of
stewed white beans, individual beans visible in red sauce").

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

**Yöntem**: Sahnelenmiş (kompozit) test çifti — Wikimedia Commons'tan CC
lisanslı gerçek yemek fotoğraflarından, bilinen artık oranlarıyla üretilmiş
önce/sonra tepsileri (`demo/make_pair.py`, `demo/test_pairs/`).

**Sonuç** (points_per_side=24, yerel Mac):

| Yemek | Gerçek oran | Tahmin | Hata |
|---|---|---|---|
| Mercimek çorbası | 0,05 | 0,000 | 0,05 |
| Kuru fasulye | 0,62 | 0,623 | 0,003 |
| Pirinç pilavı | 0,15 | 0,114 | 0,036 |
| Çoban salata | 0,85 | 0,631 | 0,219 |

Ortalama mutlak hata ≈ 0,08. Bu, saha/tartım doğrulaması değildir; yalnızca
mekanik doğrulamadır.

## Bilinen başarısız modları

1. **Karışık dokulu yemekler** (çoban salata): SAM maskeleri parçalayabilir →
   oran düşük okunur (muhafazakâr yön; israfı az göstermez, fazla göstermez).
2. **Benzer görünümlü yemekler** (çorba ↔ kuru fasulye): CLIP karıştırabilir →
   prompt mühendisliğiyle büyük ölçüde azaltıldı; tam çözülmedi.
3. **Açı/değişen kadraj**: Önce/sonra çekim açısı farklıysa oran sapar →
   uyarı mekanizması + fotoğraf rehberi (`demo/PHOTO_GUIDE.md`).
4. **Tabak+yemek birleşik maskeler**: Bazen maske tabak halkasını içerir →
   oran şişer; çift-kırpım sınıflandırma ve kapsama deduplikasyonu ile
   azaltıldı.
5. **Çok küçük artıklar** (< görüntünün %0,4'ü): ölçülmez.

## Etik ve gizlilik

- Yüz veya kişi verisi işlenmez; yalnız tepsi görüntüsü analiz edilir.
- Öğrenci geri bildirimi anonimdir (neden kodu + opsiyonel yemek).
- Çıktılar arayüzde kalıcı **TAHMİN** damgası taşır; tartım doğrulaması
  olmadan ölçüm gibi sunulmaz.

## Gerçek saha doğrulaması planı

Pilot yemekhanede örneklem günlerinde tartımlı baseline; tahmin-tartım
düzeltme katsayısı (kalibrasyon eğrisi) çıkarılacak; `measurement_method`
alanıyla tahmin/tartım kayıtları ayrı tutulacaktır.
