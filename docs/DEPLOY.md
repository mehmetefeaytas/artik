# Deploy Kılavuzu

ARTIK'ın iki bileşeni ayrı yerlerde çalışır:

| Bileşen | Platform | Not |
|---|---|---|
| `web/` (Next.js) | Vercel | Ücretsiz plan yeterli |
| `api/` (FastAPI + modeller) | Hugging Face Spaces (Docker) | Ücretsiz CPU; analiz ~1–3 dk |

Yerel sunucu (laptop) her zaman en hızlı demo yoludur; deploy edilmiş sürüm
jüri/ziyaretçi için erişilebilir yedektir. Web, API'ye ulaşamazsa istasyon
sayfası otomatik olarak demo moduna düşer.

## 1 · API → Hugging Face Space

1. https://huggingface.co/new-space adresinde Space oluştur:
   - Space name: `artik-api` · SDK: **Docker** · Plan: **Free (CPU)**
2. Repoyu Space'e gönder (repo kökünden):

```bash
git clone https://huggingface.co/spaces/<kullanici-adi>/artik-api spaces-artik
cd spaces-artik
# Space Docker'ı kök dizindeki Dockerfile'ı arar — api/Dockerfile'ı köke kopyala
cp <artik-repo>/api/Dockerfile .
# api/ ve data/ klasörlerini de kopyala (Dockerfile bunları bekler)
cp -r <artik-repo>/api <artik-repo>/data .
git add -A && git commit -m "ARTIK API deploy" && git push
```

3. Build ~10 dk sürer (modeller imgeye gömülür). Sağlık kontrolü:
   `https://<kullanici-adi>-artik-api.hf.space/health`

Notlar:
- `ARTIK_SAM_POINTS=16` (imge içinde) — CPU'da hız/doğruluk dengesi.
- SQLite (`api/artik.db`) Space yeniden başladığında sıfırlanır; demo için kabul
  edilir, kalıcılık için HF persistent storage veya harici DB gerekir.

## 2 · Web → Vercel

1. https://vercel.com/new → GitHub'daki `mehmetefeaytas/artik` reposunu içe aktar
2. Ayarlar:
   - Root Directory: `web`
   - Environment Variables → `NEXT_PUBLIC_API_URL` =
     `https://<kullanici-adi>-artik-api.hf.space`
3. Deploy

Alternatif (CLI): `cd web && vercel --prod` (önce `vercel login`)

## 3 · Yerel demo (en hızlı)

```bash
# Terminal 1 — API
cd api && uv sync && uv run uvicorn app.main:app --port 8000

# Terminal 2 — Web
cd web && npm install && npm run dev
# http://localhost:3000
```

## Doğrulama kontrol listesi

- [ ] `GET /health` → `{"models_ready": true}`
- [ ] İstasyon: demo menüsü + demo çifti → analiz sonucu geliyor
- [ ] Panel: senaryo grafikleri + öneriler doluyor
- [ ] API kapalıyken istasyon demo moduna düşüyor
- [ ] TR/EN geçişi çalışıyor
