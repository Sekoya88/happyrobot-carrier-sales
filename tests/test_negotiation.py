import pytest
from domain.entities import NegotiationSession
from domain.services import NegotiationService


def test_accept_within_ceiling():
    svc = NegotiationService(ceiling_pct=0.05)
    session = NegotiationSession(initial_rate=3000.0, round_count=0)
    result = svc.evaluate_counter(session, counter_offer=3100.0)
    assert result.accepted is True
    assert result.agreed_rate == 3100.0


def test_reject_above_ceiling():
    svc = NegotiationService(ceiling_pct=0.05)
    session = NegotiationSession(initial_rate=3000.0, round_count=0)
    result = svc.evaluate_counter(session, counter_offer=3200.0)
    assert result.accepted is False
    assert result.counter_offer is not None


def test_no_deal_after_three_rounds():
    svc = NegotiationService(ceiling_pct=0.05)
    session = NegotiationSession(initial_rate=3000.0, round_count=3)
    result = svc.evaluate_counter(session, counter_offer=3200.0)
    assert result.accepted is False
    assert result.outcome == "no_deal"
