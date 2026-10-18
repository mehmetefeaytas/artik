"""ARTIK API — FastAPI uygulaması.

Uçlar:
  GET  /health     servis + model durumu
  GET  /menu       senaryo menü kataloğu (istasyon sayfası için)
  POST /analyze    önce/sonra tepsi fotoğrafı -> öğe bazlı artık tahmini
  POST /feedback   öğrenci neden kodu kaydı
  GET  /stats      panel agregasyonu (senaryo + gerçek ayrı)
"""

from __future__ import annotations

import base64
import io
import json
from contextlib import asynccontextmanager
from datetime import date as date_type
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

from . import scenario
from . import stats as stats_mod
from .overlay import annotate
from .store import Store
from .vision import TrayAnalyzer, preprocess

DB_PATH = Path(__file__).resolve().parent.parent / "artik.db"
ALLOWED_REASONS = {"porsiyon_buyuk", "tadi", "sicaklik", "cesit_tekrar", "acele", "diger"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.store = Store(str(DB_PATH))
    try:
        app.state.analyzer = TrayAnalyzer()
        app.state.models_ready = True
    except Exception as exc:  # model yüklenemezse servis ayakta kalır, /analyze 503 döner
        app.state.analyzer = None
        app.state.models_ready = False
        app.state.model_error = str(exc)
    yield


app = FastAPI(title="ARTIK API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _load_image(data: bytes) -> Image.Image:
    try:
        return Image.open(io.BytesIO(data))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Geçersiz görüntü: {exc}") from exc


def _parse_menu(menu_raw: str) -> list[dict]:
    try:
        menu = json.loads(menu_raw)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail=f"menu JSON çözümlenemedi: {exc}") from exc
    if not isinstance(menu, list) or not menu:
        raise HTTPException(status_code=400, detail="menu boş olmayan bir liste olmalı")
    seen: set[str] = set()
    for it in menu:
        for field in ("key", "name_tr", "name_en"):
            if not it.get(field):
                raise HTTPException(status_code=400, detail=f"menu öğesinde '{field}' eksik")
        if it["key"] in seen:
            raise HTTPException(status_code=400, detail=f"menu anahtarı tekrarlı: {it['key']}")
        seen.add(it["key"])
    return menu


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "models_ready": getattr(app.state, "models_ready", False),
        "model_error": getattr(app.state, "model_error", None),
        "scenario_records": len(scenario.measurements()),
    }


@app.get("/menu")
def menu() -> dict:
    items = scenario.menu_catalog()
    return {"items": items, "note": "Senaryo menü kataloğu; istasyonda günün menüsü seçilir."}


@app.post("/analyze")
async def analyze(
    before: UploadFile = File(...),
    after: UploadFile = File(...),
    menu: str = Form(...),
    site: str = Form("pilot-universite"),
    meal: str = Form("ogle"),
    date: str = Form(default=None),
    save: bool = Form(False),
) -> dict:
    if not getattr(app.state, "models_ready", False):
        raise HTTPException(
            status_code=503, detail="Modeller hazır değil (başlangıçta yüklenemedi)"
        )

    menu_list = _parse_menu(menu)
    b_img = _load_image(await before.read())
    a_img = _load_image(await after.read())

    result = app.state.analyzer.analyze_pair(b_img, a_img, menu_list)

    order = [it["key"] for it in menu_list]
    ann_b = annotate(
        preprocess(b_img),
        result.pop("segments_before"),
        order,
        "ÖNCE — servis",
        "Görüntüden tahmin; tartım doğrulaması gerekir",
    )
    ann_a = annotate(
        preprocess(a_img),
        result.pop("segments_after"),
        order,
        "SONRA — iade",
        "Görüntüden tahmin; tartım doğrulaması gerekir",
    )
    result["annotated_before_b64"] = base64.b64encode(ann_b).decode()
    result["annotated_after_b64"] = base64.b64encode(ann_a).decode()

    if save:
        d = date or date_type.today().isoformat()
        for it in result["items"]:
            if it["estimated_leftover_g"] is None:
                continue
            app.state.store.insert_measurement(
                site=site,
                meal=meal,
                date=d,
                item_key=it["key"],
                item_name_tr=it["name_tr"],
                portion_g=it["portion_g"],
                leftover_ratio=it["leftover_ratio"],
                estimated_leftover_g=it["estimated_leftover_g"],
            )
    return result


@app.post("/feedback")
async def feedback(
    reason_code: str = Form(...),
    item_key: str | None = Form(None),
    site: str = Form("pilot-universite"),
    meal: str = Form("ogle"),
    date: str = Form(default=None),
) -> dict:
    if reason_code not in ALLOWED_REASONS:
        raise HTTPException(status_code=400, detail=f"Bilinmeyen neden kodu: {reason_code}")
    app.state.store.insert_feedback(
        site=site,
        meal=meal,
        date=date or date_type.today().isoformat(),
        item_key=item_key,
        reason_code=reason_code,
    )
    return {"status": "ok"}


@app.get("/stats")
def stats(days: int = 56) -> dict:
    return stats_mod.build_stats(app.state.store, days=days)
