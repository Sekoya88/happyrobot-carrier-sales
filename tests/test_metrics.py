import pytest
import asyncio
from infrastructure.call_repository import CallRepository
from infrastructure.metrics_service import MetricsService
from domain.entities import CallRecord, CallOutcome, Sentiment


@pytest.fixture
def repo(tmp_path):
    db = str(tmp_path / "test.db")
    r = CallRepository(db_path=db, auto_seed=False)
    asyncio.get_event_loop().run_until_complete(r.init_db())
    return r


def test_metrics_after_two_calls(repo):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(repo.save(CallRecord(
        load_id="LD-001", mc_number="123456",
        outcome=CallOutcome.booked, sentiment=Sentiment.positive,
        agreed_rate=3100.0, num_negotiations=1
    )))
    loop.run_until_complete(repo.save(CallRecord(
        load_id="LD-002", mc_number="654321",
        outcome=CallOutcome.no_deal, sentiment=Sentiment.negative,
        agreed_rate=None, num_negotiations=3
    )))
    svc = MetricsService(repo)
    metrics = loop.run_until_complete(svc.compute())
    assert metrics["total_calls"] == 2
    assert metrics["booked"] == 1
    assert metrics["conversion_rate"] == 0.5
    assert "calls_today" in metrics
    assert "calls_yesterday" in metrics
    assert "avg_duration_seconds" in metrics
    assert "top_rate" in metrics
    assert metrics["calls_today"] == 2        # both fixture records saved today
    assert metrics["calls_yesterday"] == 0    # none saved yesterday
    assert metrics["avg_duration_seconds"] is None  # no duration in fixture data
    assert metrics["top_rate"] == 3100.0
