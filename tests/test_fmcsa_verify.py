import pytest

from infrastructure.fmcsa_client import FMCSAClient, INVALID_MC_STATUS


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr("infrastructure.fmcsa_client.settings.fmcsa_mock_fallback", True)
    return FMCSAClient()


@pytest.mark.asyncio
async def test_verify_invalid_format_rejected(client):
    for raw in ("0000", "abc", "12", "MC-12", "a b c", ""):
        r = await client.verify(raw)
        assert r.eligible is False
        assert r.status == INVALID_MC_STATUS


@pytest.mark.asyncio
async def test_verify_normalized_then_mock(client):
    r = await client.verify("MC 123 456")
    assert r.eligible is True
    assert r.mc_number == "123456"


@pytest.mark.asyncio
async def test_verify_revoked_mock(client):
    r = await client.verify("000000")
    assert r.eligible is False
    assert r.status == "REVOKED"
