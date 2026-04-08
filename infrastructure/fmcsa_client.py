import httpx
import logging
from domain.entities import CarrierVerification
from app.config import settings

logger = logging.getLogger(__name__)

MOCK_CARRIERS = {
    "123456": CarrierVerification(
        mc_number="123456",
        eligible=True,
        status="ACTIVE",
        dot_number="987654",
        legal_name="Demo Carrier LLC",
    ),
    "000000": CarrierVerification(
        mc_number="000000",
        eligible=False,
        status="REVOKED",
        dot_number=None,
        legal_name="Revoked Carrier Inc",
    ),
}


class FMCSAClient:
    def __init__(self):
        self.base_url = settings.fmcsa_base_url
        self.api_key = settings.fmcsa_api_key
        self.timeout = 5.0

    async def verify(self, mc_number: str) -> CarrierVerification:
        if settings.fmcsa_mock_fallback:
            return self._mock(mc_number)
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(
                    f"{self.base_url}/{mc_number}",
                    params={"webKey": self.api_key},
                )
                resp.raise_for_status()
                data = resp.json().get("content", {}).get("carrier", {})
                return CarrierVerification(
                    mc_number=mc_number,
                    eligible=data.get("allowedToOperate", "N") == "Y",
                    status=data.get("statusCode", "UNKNOWN"),
                    dot_number=str(data.get("dotNumber", "")),
                    legal_name=data.get("legalName", ""),
                )
        except Exception as exc:
            logger.warning("FMCSA API error for MC %s: %s — using mock", mc_number, exc)
            return self._mock(mc_number)

    def _mock(self, mc_number: str) -> CarrierVerification:
        if mc_number in MOCK_CARRIERS:
            return MOCK_CARRIERS[mc_number]
        return CarrierVerification(
            mc_number=mc_number,
            eligible=True,
            status="ACTIVE",
            dot_number="000001",
            legal_name=f"Carrier MC-{mc_number}",
        )
