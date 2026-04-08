from infrastructure.call_repository import CallRepository


class MetricsService:
    def __init__(self, repo: CallRepository):
        self.repo = repo

    async def compute(self) -> dict:
        records = await self.repo.all()
        total = len(records)
        if total == 0:
            return {
                "total_calls": 0,
                "booked": 0,
                "no_deal": 0,
                "abandoned": 0,
                "conversion_rate": 0.0,
                "avg_rate_variance_pct": None,
                "sentiment_breakdown": {},
                "recent_calls": [],
            }

        booked = [r for r in records if r["outcome"] == "booked"]
        no_deal = [r for r in records if r["outcome"] == "no_deal"]
        abandoned = [r for r in records if r["outcome"] == "abandoned"]

        sentiment_counts: dict[str, int] = {}
        for r in records:
            sentiment_counts[r["sentiment"]] = (
                sentiment_counts.get(r["sentiment"], 0) + 1
            )

        return {
            "total_calls": total,
            "booked": len(booked),
            "no_deal": len(no_deal),
            "abandoned": len(abandoned),
            "conversion_rate": round(len(booked) / total, 4),
            "avg_rate_variance_pct": None,
            "sentiment_breakdown": sentiment_counts,
            "recent_calls": records[:10],
        }
