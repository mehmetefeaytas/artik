"""Senaryo (sentetik) veri yükleyici.

ÖNEMLİ: data/scenario altındaki her şey SENARYO verisidir; saha ölçümü değildir.
Üretici: data/generate_scenario.py (sabit tohumlu, yeniden üretilebilir).
"""

from __future__ import annotations

import json
import os
from functools import lru_cache

_DEFAULT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
DATA_DIR = os.environ.get("ARTIK_DATA_DIR", _DEFAULT_DIR)


def _load(name: str):
    path = os.path.join(DATA_DIR, "scenario", name)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def menu_catalog() -> list[dict]:
    data = _load("menu.json")
    return data["items"] if data else []


@lru_cache(maxsize=1)
def measurements() -> list[dict]:
    data = _load("measurements.json")
    if not data:
        return []
    return data["measurements"] if isinstance(data, dict) else data


@lru_cache(maxsize=1)
def feedback() -> list[dict]:
    data = _load("feedback.json")
    return data if data else []


def scenario_meta() -> dict:
    data = _load("measurements.json")
    return data.get("meta", {}) if isinstance(data, dict) else {}


def clear_caches() -> None:
    menu_catalog.cache_clear()
    measurements.cache_clear()
    feedback.cache_clear()
