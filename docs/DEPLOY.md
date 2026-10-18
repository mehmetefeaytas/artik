# Deploy Kılavuzu

ARTIK'ın iki bileşeni ayrı yerlerde çalışır:

| Bileşen | Platform | Durum |
|---|---|---|
| `web/` (Next.js) | GitHub Pages (statik export) | **Yayında**: https://mehmetefeaytas.github.io/artik/ |
| `api/` (FastAPI + modeller) | Yerel laptop (+ Cloudflare tüneli) | Canlı demo sırasında çalışır |

## Canlı demo (tek komut)

```bash
./demo/live_demo.sh          # API + tünel + yayınlanmış siteyi canlı moda geçir
./demo/live_demo.sh --local  # Sadece yerel API + web (ağ bağımlılığı yok)
./demo/live_demo.sh --down   # Tüneli kapat
```

`live_demo.sh` ne yapar:
1. API'yi yerelde başlatır (`:8000`)
2. Cloudflare hızlı tüneli açar (her çalıştırmada yeni URL)
3. Yayınlanmış siteyi `NEXT_PUBLIC_API_URL=<tünel>` ile yeniden oluşturup
   gh-pages dalına iter → **GitHub Pages'teki site canlı API'ye bağlanır**
4. Yerel web'i de (`:3000`) başlatır

Tünel kapalıyken site otomatik **demo moduna** düşer (ön-hesaplanmış sonuç);
bu bilinçli bir tasarım kararıdır — yayınlanan bağlantı asla kırılmaz.

> Not (Ekim 2026): Hugging Face dinamik (Docker/Gradio) Space'ler ücretsiz
> hesapta PRO gerektiriyor; bu yüzden API yerel + tünel modeliyle yayında.
> Alternatifler (HF PRO, Cloud Run) `api/Dockerfile` hazır olduğu için
> dakikalar içinde devreye alınabilir.

## Manuel statik yayını

```bash
cd web
STATIC_EXPORT=1 NEXT_PUBLIC_BASE_PATH=/artik npm run build
# out/ içeriğini gh-pages dalına it (.nojekyll ile)
```

## Yerel geliştirme

```bash
# API (port 8000)
cd api && uv sync && uv run uvicorn app.main:app --reload

# Web (port 3000)
cd web && npm install && npm run dev
```

İlk API çalıştırması SAM checkpoint'ini (~375 MB) ve CLIP'i indirir.
Analiz yerel Mac'te ~30–70 sn sürer (2 görüntü); tünel üzerinden ~75 sn.

## Doğrulama kontrol listesi

- [ ] `GET /health` → `{"models_ready": true}`
- [ ] İstasyon: demo menüsü + demo çifti → analiz sonucu geliyor
- [ ] Panel: senaryo grafikleri + öneriler doluyor
- [ ] API kapalıyken istasyon demo moduna düşüyor
- [ ] TR/EN geçişi çalışıyor
- [ ] Yayınlanmış site: tünel açıkken menü listesi doluyor
