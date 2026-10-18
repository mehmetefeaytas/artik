# ARTIK — Pitch Destesi (12 slayt) + Konuşmacı Notları

Süre hedefi: 5 dakika sunum + soru-cevap. Kalın başlıklar slayt metni,
_italik_ satırlar konuşmacı notudur.

---

## S1 · Kapak

**ARTIK — Tabakta ne kalıyorsa, bütçeden o gidiyor.**

_Ymekhane tabak artığı analiz ve karar destek sistemi. Climathon 2026._
_Bağlantılar: mehmetefeaytas.github.io/artik · github.com/mehmetefeaytas/artik_

## S2 · Problem

- **Öğrencilerin %80,3'ü** tabakta yemek bıraktığını bildiriyor
  _(Gümüşhane Üniv. 2023, n=330; nedenler: soğuk servis, tat, tekrar)_
- Gıda hizmetleri sektörü 2022'de **~290 milyon ton** atık üretti
  _(UNEP Food Waste Index 2024)_
- **SDG 12.3**: 2030'a kadar per capita gıda israfını yarıya indirmek
- COP31 hattı: **atığı 2035'e kadar yarıya indirmek**

_Tek cümle: kararlar — kaç porsiyon, hangi boyut — gerçek tüketim verisiyle
güncellenmiyor; israf sistemsel tekrarlanıyor._

## S3 · Kök neden

**Porsiyon sabit, geri bildirim yok, karar sezgide.**

- Sabit porsiyon + istenmeyen yemeği almak zorunda olma
- Artık hiç ölçülmüyor → menü planlama deneyime kalıyor
- _Hafta 1 problem tanımımızdaki codex destekli kök neden analizinden: en
  doğrudan sinyal iade hattındaki tabak artığı — karar bunu görmüyor._

## S4 · Çözüm

**ARTIK: istasyon + panel + öğrenci sesi.**

1. İade hattında kamera istasyonu — önce/sonra tepsi fotoğrafı
2. Zero-shot görüntü işleme (SAM+CLIP) — yemek bazlı artık tahmini
3. Panel — porsiyon önerileri, CO₂e/su/maliyet, QR geri bildirim

## S5 · Nasıl çalışır

**Önce → Sonra → Karar** (şema)

- SAM tepsiyi maskelere böler; CLIP maskeleri günün menüsüyle eşler
  _(eğitim yok — menü istasyondan geçer, her yemekhaneye uyarlanır)_
- Artık oranı = alan(sonra) / alan(önce); gram = oran × porsiyon
- _Vurgu: görüntüden gram TAHMİNDİR — tartım doğrulaması planı S8'de._

## S6 · Canlı demo (video veya ekran)

_2 dakikalık akış: menü seçimi → önce/sonra fotoğraf → analiz → sonuç kartları
→ panel → öneri → QR. Video: docs/DEMO_VIDEO.md senaryosu._

## S7 · Farkımız: dürüst yapay zeka

**Ne ölçüyoruz, ne varsayıyoruz — arayüzde damgalı.**

- `TAHMİN` — görüntüden gram, tartım değil
- `SENARYO` — panel geçmişi sentetik tohum, saha ölçümü değil
- `SİMÜLASYON` — etki öngörüsü aralıkla, tek sayı değil
- _Jüriye: "Sistem satmıyor, ölçüyor. Pilot kararı verinin kendisi verecek."_
- _Doğrulama: kompozit test çiftinde ort. mutlak hata ≈ 0,08 (model kartı)._

## S8 · Etki ölçümü

**Baseline → müdahale → karşılaştırma.**

- Örnek (senaryo): Ispanak %33 artık → porsiyon 260g→208g →
  **307–683 kg/180 gün** tasarruf ≈ **0,8–1,7 t CO₂e**
- Guardrail: yemek bulunamama, memnuniyet — _öğrenciyi aç bırakan
  optimizasyon başarılı sayılmaz_
- Pilot planı: örneklem tartım doğrulaması + kalibrasyon eğrisi

## S9 · Neden AI, neden şimdi

- Yüzlerce tepsi/gün — insan etiketlemesi sürdürülemez
- Zero-shot: kurum değişince model eğitimi yok, menü yeter
- COP31 Türkiye'de: kurum yemekhaneleri için yerli, açık kaynak,
  uyarlanabilir ilk örneklerden

## S10 · Manzara

**Winnow / Leanpath**: kurumsal, kapalı, pahalı, batı mutfağı odaklı.
**ARTIK**: açık kaynak (MIT), Türk menüsü, kurum-uyarlanır, dürüstlük-önce.

## S11 · Yol haritası

- **Kasım 2026**: COP31 demosu, pilot görüşmeleri
- **Ara 2026–Şub 2027**: bir üniversite yemekhanesinde baseline pilotu + tartım
- **2027**: yarım porsiyon POS, üretim fazlası/talep modülü, çoklu kurum

## S12 · Kapanış

**ARTIK — artığı görünür kılan, kararı veriye bağlayan açık kaynak istasyon.**

_Repo + demo + PDR + model kartı tek bağlantıda. Sorulara hazırım — özellikle
"sistem neyi ölçemiyor" sorusuna: /yontem sayfası tam bunun için var._

---

## Beklenen jüri soruları ve cevapları

**"Görüntüden gram ne kadar güvenilir?"**
Alan oranı iyi bir yaklaşımdır ama tahmindir; kompozit testimizde 4 yemekte
ort. ±8 puan; salata gibi parçalanan yemeklerde muhafazakâr kalır. Pilotte
örneklem tartımla kalibrasyon eğrisi çıkaracağız — şema hazır.

**"Öğrenci verisi/gizlilik?"**
Yüz işlenmez, yalnız tepsi. QR geri bildirimi anonim. KVKK notu yöntem sayfasında.

**"Winnow'dan farkınız?"**
Onlar kapalı/kurumsal SaaS; biz açık kaynak, kurum-uyarlanır zero-shot, ve
Türkiye yemekhane bağlamı. Özgünlük iddiamız "ilk AI" değil — ölçülebilir
yerel iş akışı ve dürüst çerçeve.

**"Pilot yapmadan etki nasıl kanıtlanır?"**
Kanıtlanmaz — bu yüzden panel simülasyonu aralık verir ve pilot planı
belirlidir. Prototipin işi, ölçüm altyapısını kurmak; etkiyi pilot gösterecek.
