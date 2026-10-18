"""SQLite tabanlı basit kalıcı depo: gerçek analiz kayıtları + geri bildirimler."""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime

SCHEMA = """
CREATE TABLE IF NOT EXISTS measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    site TEXT NOT NULL,
    meal TEXT NOT NULL,
    date TEXT NOT NULL,
    item_key TEXT NOT NULL,
    item_name_tr TEXT NOT NULL,
    portion_g REAL,
    leftover_ratio REAL NOT NULL,
    estimated_leftover_g REAL NOT NULL,
    source TEXT NOT NULL DEFAULT 'vision_estimate'
);
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    site TEXT NOT NULL,
    meal TEXT NOT NULL,
    date TEXT NOT NULL,
    item_key TEXT,
    reason_code TEXT NOT NULL
);
"""


class Store:
    def __init__(self, path: str) -> None:
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    @staticmethod
    def _now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds")

    def insert_measurement(
        self,
        *,
        site: str,
        meal: str,
        date: str,
        item_key: str,
        item_name_tr: str,
        portion_g: float | None,
        leftover_ratio: float,
        estimated_leftover_g: float,
    ) -> None:
        self.conn.execute(
            "INSERT INTO measurements (created_at, site, meal, date, item_key, item_name_tr,"
            " portion_g, leftover_ratio, estimated_leftover_g) VALUES (?,?,?,?,?,?,?,?,?)",
            (
                self._now(), site, meal, date, item_key, item_name_tr,
                portion_g, leftover_ratio, estimated_leftover_g,
            ),
        )
        self.conn.commit()

    def insert_feedback(
        self, *, site: str, meal: str, date: str, item_key: str | None, reason_code: str
    ) -> None:
        self.conn.execute(
            "INSERT INTO feedback (created_at, site, meal, date, item_key, reason_code)"
            " VALUES (?,?,?,?,?,?)",
            (self._now(), site, meal, date, item_key, reason_code),
        )
        self.conn.commit()

    def measurements(self) -> list[dict]:
        rows = self.conn.execute("SELECT * FROM measurements ORDER BY date").fetchall()
        return [dict(r) for r in rows]

    def feedback(self) -> list[dict]:
        rows = self.conn.execute("SELECT * FROM feedback ORDER BY date").fetchall()
        return [dict(r) for r in rows]

    def feedback_counts(self, days: int = 56) -> dict[str, int]:
        rows = self.conn.execute(
            "SELECT reason_code, COUNT(*) AS n FROM feedback GROUP BY reason_code"
        ).fetchall()
        return {r["reason_code"]: r["n"] for r in rows}
