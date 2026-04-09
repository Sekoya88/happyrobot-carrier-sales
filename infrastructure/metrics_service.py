from collections import defaultdict
from datetime import datetime, timedelta
from infrastructure.call_repository import CallRepository


class MetricsService:
    def __init__(self, repo: CallRepository):
        self.repo = repo

    async def compute(self) -> dict:
        records = await self.repo.all()
        total = len(records)

        today_str = datetime.utcnow().date().isoformat()
        yesterday_str = (datetime.utcnow().date() - timedelta(days=1)).isoformat()

        if total == 0:
            return {
                "total_calls": 0, "booked": 0, "no_deal": 0, "abandoned": 0,
                "conversion_rate": 0.0, "avg_agreed_rate": None,
                "total_revenue": 0.0, "avg_negotiations": 0.0,
                "avg_rate_variance_pct": None, "sentiment_breakdown": {},
                "calls_over_time": [], "recent_calls": [],
                "calls_today": 0, "calls_yesterday": 0,
                "avg_duration_seconds": None, "top_rate": None,
            }

        booked    = [r for r in records if r["outcome"] == "booked"]
        no_deal   = [r for r in records if r["outcome"] == "no_deal"]
        abandoned = [r for r in records if r["outcome"] == "abandoned"]

        sentiment_counts: dict[str, int] = {}
        for r in records:
            s = r["sentiment"] or "neutral"
            sentiment_counts[s] = sentiment_counts.get(s, 0) + 1

        rates = [r["agreed_rate"] for r in booked if r["agreed_rate"]]
        avg_rate = round(sum(rates) / len(rates), 2) if rates else None
        total_revenue = round(sum(rates), 2) if rates else 0.0
        avg_neg = round(sum(r["num_negotiations"] for r in records) / total, 2)

        durations = [r["duration_seconds"] for r in records if r.get("duration_seconds")]
        avg_dur = round(sum(durations) / len(durations), 1) if durations else None

        top_rate = max(rates) if rates else None

        calls_today = sum(
            1 for r in records if (r.get("created_at") or "")[:10] == today_str
        )
        calls_yesterday = sum(
            1 for r in records if (r.get("created_at") or "")[:10] == yesterday_str
        )

        return {
            "total_calls": total,
            "booked": len(booked),
            "no_deal": len(no_deal),
            "abandoned": len(abandoned),
            "conversion_rate": round(len(booked) / total, 4),
            "avg_agreed_rate": avg_rate,
            "total_revenue": total_revenue,
            "avg_negotiations": avg_neg,
            "avg_rate_variance_pct": None,
            "sentiment_breakdown": sentiment_counts,
            "calls_over_time": self._timeline(records, days=7),
            "recent_calls": records[:50],
            "calls_today": calls_today,
            "calls_yesterday": calls_yesterday,
            "avg_duration_seconds": avg_dur,
            "top_rate": top_rate,
        }

    def _timeline(self, records: list[dict], days: int) -> list[dict]:
        """Return daily call counts + booked for the last N days."""
        buckets: dict[str, dict] = {}
        today = datetime.utcnow().date()
        for i in range(days - 1, -1, -1):
            d = (today - timedelta(days=i)).isoformat()
            buckets[d] = {"date": d, "total": 0, "booked": 0}

        for r in records:
            raw = r.get("created_at") or ""
            try:
                day = raw[:10]
                if day in buckets:
                    buckets[day]["total"] += 1
                    if r["outcome"] == "booked":
                        buckets[day]["booked"] += 1
            except Exception:
                pass

        return list(buckets.values())
