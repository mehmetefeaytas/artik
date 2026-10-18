# ARTIK Demo Fotoğraf Rehberi (Gerçek Çekim)

Bu rehber, prototipin **gerçek sahne** demo görüntülerini çekmek için hazırlanmıştır.
Günlük yemeğinden önce ve sonra telefonla çekeceğin 3–4 tepsi çifti, demo videosunun
ve canlı sunumun ana malzemesi olacak.

## Ne çekiyoruz?

Her tepsi için **iki fotoğraf**:
1. **ÖNCE** — servis edildiği haliyle dolu tepsi
2. **SONRA** — yemeğin bir kısmını gerçekten yedikten sonra aynı tepsi

## Altın kurallar (doğruluk için kritik)

- **Aynı açı**: İki fotoğraf da tepsiye **yukarıdan (90°)**, mümkünse aynı yükseklikten
- **Aynı yer ve ışık**: Aynı masa, aynı ışık kaynağı; gölge düşürme
- **Aynı düzen**: Tabaklar/tepsi iki karede aynı konumda (yemeğe başlamadan önce kadrajı belirle)
- **Tek tepsi kadrajda**: Kenarlar görünsün ama masa fazla yer kaplamasın
- **Telefonu düz tut**: Eğik çekim alan oranını bozar
- Karartma/filtre yok, HDR kapalı olabilir; flaş kullanma

## Yemek seçimi (model davranışı biliniyor)

| İyi segment olur (önerilir) | Zor (çek ama demosuna güvenme) |
|---|---|
| Pirinç pilavı, bulgur | Karışık çoban/mevsim salata (parçalanıyor) |
| Kuru fasulye, nohut | Çok küçük artıklar (kraker kırıntısı gibi) |
| Köfte, tavuk, balık (parça ana yemek) | İki yemeğin birbirine karıştığı tabak |
| Çorba (kase) | Yassı aynı renkli soslar |

**Demo çekimi için ideal menü**: çorba + kuru fasulye + pilav + köfte/tavuk gibi
4 görsel olarak ayrık yemek.

## Senaryo çeşitliliği (4–5 çift çek)

| Çift | Senaryo | Amaç |
|---|---|---|
| A | Her şey yarı yarıya yenmiş | Dengeli durum |
| B | Ana yemek tamamen bitmiş, pilav kalmış | Farklı oranlar |
| C | Bir yemek neredeyse hiç yenmemiş | "Neden bıraktın?" akışını göster |
| D | Her şey bitmiş (temiz tabak) | Sıfır artık durumu |
| E | Yarım porsiyon görünümlü tabak | Porsiyon önerisi hikayesi |

## Çektikten sonra

Dosyaları şu şemayla `demo/real_shots/` klasörüne koy:

```
demo/real_shots/
  A_before.jpg   A_after.jpg
  B_before.jpg   B_after.jpg   ...
```

Sonra test et (api/ altından):

```bash
uv run python scripts/test_real.py   # (Gün 2'de eklenecek)
```

## Hatırlatma

- Bu fotoğraflar **kendi çekimindir**; uygulama içinde "sahnelenmiş demo" olarak
  etiketlenecek, saha ölçümü sayılmayacaktır.
- Yemeği gerçekten yiyerek çek — "sahte artık" (tabağa geri koymak) doğal görünmeyebilir
  ve model yüzey farkını yakalayabilir.
