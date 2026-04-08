import aiosqlite
import random
from datetime import datetime, timedelta
from domain.entities import CallRecord, CallOutcome, Sentiment
from typing import Optional


SEED_RECORDS = [
    # Booked calls — various lanes, positive sentiment
    ("MC-10021", "LD-001", "booked",    "positive", 3150.0, 1, 210, "Chicago, IL → Dallas, TX"),
    ("MC-30045", "LD-002", "booked",    "positive", 3400.0, 0, 145, "Chicago, IL → Dallas, TX"),
    ("MC-55710", "LD-003", "booked",    "positive", 2680.0, 2, 320, "Los Angeles, CA → Phoenix, AZ"),
    ("MC-77832", "LD-005", "booked",    "positive", 4100.0, 1, 190, "New York, NY → Miami, FL"),
    ("MC-20019", "LD-006", "booked",    "neutral",  2900.0, 3, 275, "Dallas, TX → Houston, TX"),
    ("MC-44301", "LD-007", "booked",    "positive", 3780.0, 1, 160, "Chicago, IL → Atlanta, GA"),
    ("MC-88123", "LD-008", "booked",    "positive", 5200.0, 0, 135, "Los Angeles, CA → Seattle, WA"),
    ("MC-65432", "LD-010", "booked",    "neutral",  3100.0, 2, 240, "Chicago, IL → Dallas, TX"),
    ("MC-11290", "LD-011", "booked",    "positive", 2450.0, 1, 180, "Denver, CO → Salt Lake City, UT"),
    ("MC-39871", "LD-012", "booked",    "positive", 4600.0, 0, 120, "New York, NY → Boston, MA"),
    # No deal — negotiation failed
    ("MC-22567", "LD-001", "no_deal",   "negative", None,   3, 390, "Carrier wanted 15% over rate"),
    ("MC-33890", "LD-004", "no_deal",   "negative", None,   3, 410, "Could not agree on equipment"),
    ("MC-12045", "LD-009", "no_deal",   "neutral",  None,   3, 360, "Rate too low for the lane"),
    ("MC-71234", "LD-003", "no_deal",   "negative", None,   3, 425, "Carrier unresponsive after 3 rounds"),
    ("MC-50099", "LD-005", "no_deal",   "neutral",  None,   2, 295, "Load no longer available"),
    # Abandoned — carrier hung up or no response
    ("MC-90011", None,     "abandoned", "negative", None,   0,  45, None),
    ("MC-43210", "LD-002", "abandoned", "neutral",  None,   1,  90, None),
    (None,       None,     "abandoned", "negative", None,   0,  20, None),
    ("MC-18765", None,     "abandoned", "neutral",  None,   0,  35, None),
    ("MC-27654", "LD-007", "abandoned", "negative", None,   1,  80, None),
    # More booked with different days spacing
    ("MC-60001", "LD-013", "booked",    "positive", 3350.0, 1, 200, "Memphis, TN → Nashville, TN"),
    ("MC-60002", "LD-014", "booked",    "positive", 2750.0, 0, 155, "Phoenix, AZ → Las Vegas, NV"),
    ("MC-60003", "LD-015", "no_deal",   "neutral",  None,   2, 310, "No matching loads available"),
    ("MC-60004", "LD-016", "booked",    "positive", 4250.0, 1, 175, "Atlanta, GA → Charlotte, NC"),
    ("MC-60005", "LD-017", "abandoned", "negative", None,   0,  30, None),
]


class CallRepository:
    def __init__(self, db_path: str = "calls.db"):
        self.db_path = db_path

    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS calls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    load_id TEXT,
                    mc_number TEXT,
                    outcome TEXT NOT NULL,
                    sentiment TEXT NOT NULL,
                    agreed_rate REAL,
                    num_negotiations INTEGER NOT NULL DEFAULT 0,
                    duration_seconds INTEGER,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()

            cursor = await db.execute("SELECT COUNT(*) FROM calls")
            row = await cursor.fetchone()
            if row[0] == 0:
                await self._seed(db)

    async def _seed(self, db):
        """Insert realistic demo data spread over the last 7 days."""
        now = datetime.utcnow()
        total = len(SEED_RECORDS)
        for i, rec in enumerate(SEED_RECORDS):
            mc, load_id, outcome, sentiment, rate, rounds, duration, notes = rec
            # Spread records across last 7 days with some variance
            offset_days = (total - i - 1) / total * 7
            offset_hours = random.uniform(0, 8)
            ts = now - timedelta(days=offset_days, hours=offset_hours)
            await db.execute(
                """INSERT INTO calls
                   (load_id, mc_number, outcome, sentiment, agreed_rate,
                    num_negotiations, duration_seconds, notes, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (load_id, mc, outcome, sentiment, rate, rounds, duration, notes,
                 ts.strftime("%Y-%m-%d %H:%M:%S")),
            )
        await db.commit()

    async def save(self, record: CallRecord) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """INSERT INTO calls
                   (load_id, mc_number, outcome, sentiment, agreed_rate,
                    num_negotiations, duration_seconds, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    record.load_id,
                    record.mc_number,
                    record.outcome.value,
                    record.sentiment.value,
                    record.agreed_rate,
                    record.num_negotiations,
                    record.duration_seconds,
                    record.notes,
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
