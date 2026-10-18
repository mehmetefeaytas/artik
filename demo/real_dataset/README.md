# Gerçek Yemekhane Tepsisi Veri Seti (Padova/UNIMIB)

## Kaynak

Bu veri seti, Padova Üniversitesi "Food Recognition and Leftover Estimation"
projesinin MIT lisanslı GitHub deposundan alınmıştır:

- Depo: https://github.com/Piero24/Food-recognition-and-leftover-estimation
- Lisans: MIT © 2023 Andrea Pietrobon
- Orijinal veri: Milano-Bicocca Üniversitesi (UNIMIB) yemekhane tepsileri;
  Ciocca, Napoletano, Schettini (2015), *Food Recognition and Leftover
  Estimation for Daily Diet Monitoring*, ICIAP 2015 Workshops veri seti
  geleneğinden.

## İçerik

- `tray1..tray8`: her tepsi için
  - `food_image.jpg` — yemek öncesi (servis) fotoğrafı (1280×960)
  - `leftover1..3.jpg` — aynı tepsiyin yemek sonrası (3 aşamalı) halleri
  - `masks/` — piksel hassasiyetinde yemek-ID etiketli maskeler
  - `bounding_boxes/` — yemek-ID etiketli kutular
- `tray9`: yalnız görüntüler (etiket yok)
- `food_categories.txt` — 13 sınıf taksonomisi ve tepsi kompozisyonları

## Kullanım

- Doğrulama: `api/scripts/validate_real.py` (maskelerden ground-truth oran
  çıkarır, ARTIK pipeline tahminleriyle karşılaştırır)
- Web demo çifti: `tray1/food_image.jpg` + `tray1/leftover2.jpg`

## Not

Bu fotoğraflar İtalyan üniversite yemekhanesinde çekilmiştir; Türk
yemekhanesi demo görüntüsü değildir ve "sahnelenmiş demo" olarak etiketlenir.
Gerçek saha ölçümü sayılmaz.
