from pydantic import BaseModel, field_validator
from typing import Optional, Any
from domain.entities import CallOutcome, Sentiment


class LoadOut(BaseModel):
    load_id: str
    origin: str
    destination: str
    pickup_datetime: str
    delivery_datetime: str
    equipment_type: str
    loadboard_rate: float
    notes: str
    weight: Optional[float]
    commodity_type: str
    miles: Optional[float]


class CarrierVerificationOut(BaseModel):
    mc_number: str
    eligible: bool
    status: str
    dot_number: Optional[str]
    legal_name: Optional[str]


class CallRecordIn(BaseModel):
    load_id: Optional[str] = None
    mc_number: Optional[str] = None
    outcome: CallOutcome = CallOutcome.abandoned
    sentiment: Sentiment = Sentiment.neutral
    agreed_rate: Optional[float] = None
    num_negotiations: int = 0
    duration_seconds: Optional[int] = None
    notes: Optional[str] = None

    @field_validator("outcome", mode="before")
    @classmethod
    def coerce_outcome(cls, v: Any) -> CallOutcome:
        if isinstance(v, str):
            # strip unresolved HappyRobot variable placeholders
            clean = v.strip().lower().replace("@record_call.", "")
            mapping = {"booked": CallOutcome.booked, "no_deal": CallOutcome.no_deal, "abandoned": CallOutcome.abandoned}
            return mapping.get(clean, CallOutcome.abandoned)
        return v

    @field_validator("sentiment", mode="before")
    @classmethod
    def coerce_sentiment(cls, v: Any) -> Sentiment:
        if isinstance(v, str):
            clean = v.strip().lower().replace("@record_call.", "")
            mapping = {"positive": Sentiment.positive, "neutral": Sentiment.neutral, "negative": Sentiment.negative}
            return mapping.get(clean, Sentiment.neutral)
        return v

    @field_validator("agreed_rate", mode="before")
    @classmethod
    def coerce_agreed_rate(cls, v: Any) -> Optional[float]:
        if v is None or v == "" or (isinstance(v, str) and v.startswith("@")):
            return None
        try:
            return float(v)
        except (ValueError, TypeError):
            return None

    @field_validator("num_negotiations", mode="before")
    @classmethod
    def coerce_num_negotiations(cls, v: Any) -> int:
        if v is None or (isinstance(v, str) and v.startswith("@")):
            return 0
        try:
            return int(float(str(v)))
        except (ValueError, TypeError):
            return 0


class CallRecordOut(CallRecordIn):
    id: int


class MetricsOut(BaseModel):
    total_calls: int
    booked: int
    no_deal: int
    abandoned: int
    conversion_rate: float
    avg_agreed_rate: Optional[float]
    total_revenue: float
    avg_negotiations: float
    avg_rate_variance_pct: Optional[float]
    sentiment_breakdown: dict
    calls_over_time: list
    recent_calls: list
