# ARTIK API — Hugging Face Spaces (Docker) için
# Yerel geliştirme için gerekmez; bkz. README.

FROM python:3.12-slim

WORKDIR /app

ENV HF_HOME=/app/hf \
    ARTIK_SAM_POINTS=16 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends libglib2.0-0 curl \
    && rm -rf /var/lib/apt/lists/*

COPY api/pyproject.toml api/uv.lock ./api/
COPY api/app ./api/app
COPY data ./data

RUN pip install --no-cache-dir uv \
    && cd api \
    && uv sync --frozen --no-dev

# Modelleri imgeye önden yükle (soğuk başlatmayı hızlandırır)
RUN cd api \
    && uv run python -c "from app.vision import _ensure_sam_checkpoint; _ensure_sam_checkpoint()" \
    && uv run python -c "from transformers import CLIPModel, CLIPProcessor; \
CLIPModel.from_pretrained('openai/clip-vit-base-patch32'); \
CLIPProcessor.from_pretrained('openai/clip-vit-base-patch32')"

EXPOSE 7860

HEALTHCHECK --interval=60s --timeout=30s --start-period=180s --retries=3 \
    CMD curl -sf http://localhost:7860/health || exit 1

CMD ["uv", "run", "--directory", "api", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
