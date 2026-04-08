from pydantic import BaseModel
from typing import Optional
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
