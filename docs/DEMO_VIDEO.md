# Demo Videosu Senaryosu (~2,5 dk)

Çekim: ekran kaydı (QuickTime / OBS) + gerçek tepsi çekimleri (demo/PHOTO_GUIDE.md).
Yerel modda çek (`./demo/live_demo.sh --local`) — analiz ~40 sn; kurguda 4–6x hızlandır.

| Zaman | Görüntü | Anlatım (TR) |
|---|---|---|
| 0:00–0:15 | Kara ekran + sayılar | "Üniversite yemekhanesinde her üç öğrenciden ikisi tabakta yemek bırakıyor. %80,3. Bırakılan her gram, üretimindeki su ve enerjiyle birlikte çöpe gidiyor." |
| 0:15–0:30 | /istasyon, menü seçimi | "ARTIK istasyonu: önce günün menüsünü seçiyoruz — dört yemek, standart porsiyonlarıyla." |
| 0:30–0:55 | Önce/sonra fotoğraflar (gerçek çekim!) | "Serviste ve iadede, aynı açıdan iki fotoğraf. Fark henüz görünmez — ARTIK görünür kılıyor." |
| 0:55–1:25 | Analiz çalışıyor (hızlandırılmış), maske overlay animasyonu | "SAM tepsiden yemek maskelerini çıkarıyor, CLIP her maskeyi menüdeki yemeğle eşliyor. Eğitim yok: menü değişince model de değil, sadece etiketler değişiyor." |
| 1:25–1:45 | Sonuç kartları | "Kuru fasulyenin %62'si kalmış — tahmini 172 gram. Pilav neredeyse bitmiş. Çorba sıfır. Her değer TAHMİN damgalı: tartım doğrulaması pilotte yapılacak." |
| 1:45–2:05 | /panel: trend + sıralama | "Panelde sekiz haftalık geçmiş: en çok artık bırakılan yemekler, neden kodları — 'porsiyon büyüktü' başı çekiyor. Bu geçmiş SENARYO verisi; gerçek kayıtlar ayrı bölümde birikiyor." |
| 2:05–2:25 | Öneri kartı + simülasyon | "Ispanak %33 artık. Öneri: porsiyonu 260'tan 208 grama indir. Simülasyon 307–683 kilogram tasarruf diyor — aralık raporluyoruz, tek parlak sayı değil." |
| 2:25–2:40 | /geri-bildirim (telefon) | "Öğrenci iadede QR'ı okutup tek dokunuşla nedenini söylüyor. Menü kararı artık sezgiye değil, bu akışa dayanıyor." |
| 2:40–2:55 | /yontem | "Ve dürüstlük sayfası: ne ölçüyoruz, ne varsayıyoruz, nerede hata payı var — hepsi açık. Çünkü sürdürülebilirlikte güven, parlak demodan önemli." |
| 2:55–3:00 | Kapanış ekranı (repo + link) | "ARTIK. Açık kaynak. Tabakta ne kaldığını görünür kılıyoruz — ki bütçeden gitmesin." |

## Çekim notları

- Sonuç kartlarındaki sayılar gerçek analiz çıktısıyla eşleşsin (kurguda
  altyazı uydurma)
- Analiz beklerken progress bar'ı kesme — hızlandırılmış bekleme izleyiciye
  "gerçekten çalışıyor" hissi verir
- Sonuna GitHub repo + yayınlanmış site linki (5 sn kare)
- Aynı senaryonun İngilizce versiyonu COP31 için çekilebilir (arayüzde EN geçişi var)
