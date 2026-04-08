import aiosqlite
from domain.entities import CallRecord
from typing import Optional


class CallRepository:
    def __init__(self, db_path: str = "calls.db"):
        self.db_path = db_path

    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS calls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    load_id TEXT,
                    mc_number TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    sentiment TEXT NOT NULL,
                    agreed_rate REAL,
                    num_negotiations INTEGER NOT NULL DEFAULT 0,
                    duration_seconds INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()

    async def save(self, record: CallRecord) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """INSERT INTO calls
                   (load_id, mc_number, outcome, sentiment, agreed_rate,
                    num_negotiations, duration_seconds)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    record.load_id,
                    record.mc_number,
                    record.outcome.value,
                    record.sentiment.value,
                    record.agreed_rate,
                    record.num_negotiations,
                    record.duration_seconds,
                ),
            )
            await db.commit()
            return cursor.lastrowid

    async def all(self) -> list[dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM calls ORDER BY created_at DESC"
            )
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]
