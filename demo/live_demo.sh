#!/usr/bin/env bash
# ARTIK canlı demo kurulumu
#
# Kullanım:
#   ./demo/live_demo.sh          → API + tünel + yayınlanmış siteyi canlı moda geçir
#   ./demo/live_demo.sh --down   → Tüneli kapat (site demo moduna döner)
#   ./demo/live_demo.sh --local  → Sadece yerel API + web (tünel yok)
#
# Gereksinim: api/ altında `uv sync` yapılmış, web/ altında `npm install`
# yapılmış olmalı. cloudflared kurulu olmalı (brew install cloudflared).

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
API_PORT=8000
WEB_PORT=3000
TUNNEL_LOG=/tmp/artik_tunnel.log
API_LOG=/tmp/artik_api.log
WEB_LOG=/tmp/artik_web.log

say() { printf "\033[1;32m▶\033[0m %s\n" "$1"; }

cleanup() {
  pkill -f "cloudflared tunnel --url http://localhost:${API_PORT}" 2>/dev/null || true
  echo
  say "Tünel kapatı. Yayınlanmış site demo moduna dönmek için: ./demo/live_demo.sh --republish-demo"
}

start_api() {
  say "API başlatılıyor (port ${API_PORT})…"
  (cd "$ROOT/api" && nohup uv run uvicorn app.main:app --port "$API_PORT" > "$API_LOG" 2>&1 &)
  for i in $(seq 1 40); do
    if curl -sf "http://localhost:${API_PORT}/health" > /dev/null 2>&1; then
      say "API hazır: http://localhost:${API_PORT}"
      return 0
    fi
    sleep 2
  done
  echo "API ayağa kalkmadı — ${API_LOG} dosyasına bak." >&2
  exit 1
}

start_web() {
  say "Web başlatılıyor (port ${WEB_PORT})…"
  (cd "$ROOT/web" && nohup npm run dev -- --port "$WEB_PORT" > "$WEB_LOG" 2>&1 &)
  for i in $(seq 1 30); do
    if curl -sf "http://localhost:${WEB_PORT}" > /dev/null 2>&1; then
      say "Web hazır: http://localhost:${WEB_PORT}"
      return 0
    fi
    sleep 2
  done
  echo "Web ayağa kalkmadı — ${WEB_LOG} dosyasına bak." >&2
  exit 1
}

start_tunnel() {
  say "Cloudflare tüneli açılıyor…"
  cloudflared tunnel --url "http://localhost:${API_PORT}" > "$TUNNEL_LOG" 2>&1 &
  TUNNEL_PID=$!
  local url=""
  for i in $(seq 1 30); do
    url=$(grep -oE "https://[a-z0-9-]+\.trycloudflare\.com" "$TUNNEL_LOG" 2>/dev/null | head -1 || true)
    if [ -n "$url" ]; then break; fi
    sleep 2
  done
  if [ -z "$url" ]; then
    echo "Tünel URL'si alınamadı — ${TUNNEL_LOG} dosyasına bak." >&2
    exit 1
  fi
  say "Tünel hazır: $url"
  echo "$url" > /tmp/artik_tunnel_url
  # Tünelin dışarıdan erişilebilir olduğunu doğrula
  sleep 5
  if curl -sf "$url/health" > /dev/null 2>&1; then
    say "Dışarıdan /health doğrulandı ✓"
  else
    say "UYARI: tünel /health yanıt vermedi — yine de devam ediliyor"
  fi
}

republish_web() {
  local api_url="$1"
  say "Yayınlanmış site yeniden oluşturuluyor (API: ${api_url})…"
  rm -rf "$ROOT/web/.next"
  (cd "$ROOT/web" && STATIC_EXPORT=1 NEXT_PUBLIC_BASE_PATH=/artik NEXT_PUBLIC_API_URL="$api_url" npm run build > /tmp/artik_build.log 2>&1)
  rm -rf /tmp/ghpages && mkdir -p /tmp/ghpages
  cp -r "$ROOT/web/out/." /tmp/ghpages/
  touch /tmp/ghpages/.nojekyll
  (cd /tmp/ghpages \
    && git init -b gh-pages -q \
    && git remote add origin https://github.com/mehmetefeaytas/artik.git \
    && git add -A \
    && git commit -q -m "canlı API tüneli: ${api_url}" \
    && git push -f -q origin gh-pages)
  say "Yayınlandı: https://mehmetefeaytas.github.io/artik/"
  say "GitHub Pages güncellemesi ~1 dk içinde yayına düşer."
}

case "${1:-up}" in
  --down)
    cleanup
    ;;
  --local)
    start_api
    start_web
    say "Yerel demo hazır: http://localhost:${WEB_PORT} → http://localhost:${API_PORT}"
    ;;
  --republish-demo)
    republish_web "http://localhost:8000"
    ;;
  up|*)
    trap cleanup EXIT
    start_api
    start_tunnel
    republish_web "$(cat /tmp/artik_tunnel_url)"
    start_web
    echo
    say "CANLI DEMO HAZIR"
    echo "  · Yerel:        http://localhost:${WEB_PORT}"
    echo "  · Yayınlanmış:  https://mehmetefeaytas.github.io/artik/ (canlı API'ye bağlı)"
    echo "  · API tüneli:   $(cat /tmp/artik_tunnel_url)"
    echo
    echo "Kapatmak için: Ctrl+C veya ./demo/live_demo.sh --down"
    wait
    ;;
esac
