from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class CallOutcome(str, Enum):
    booked = "booked"
    no_deal = "no_deal"
    abandoned = "abandoned"


class Sentiment(str, Enum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"


@dataclass
class Load:
    load_id: str
    origin: str
    destination: str
    pickup_datetime: str
    delivery_datetime: str
    equipment_type: str
    loadboard_rate: float
    notes: str = ""
    weight: Optional[float] = None
    commodity_type: str = ""
    num_of_pieces: Optional[int] = None
    miles: Optional[float] = None
    dimensions: str = ""


@dataclass
class CarrierVerification:
    mc_number: str
    eligible: bool
    status: str
    dot_number: Optional[str] = None
    legal_name: Optional[str] = None


@dataclass
class NegotiationSession:
    initial_rate: float
    round_count: int
    max_authorized_rate: float = field(init=False)

    def __post_init__(self):
        self.max_authorized_rate = round(self.initial_rate * 1.05, 2)


@dataclass
class NegotiationResult:
    accepted: bool
    agreed_rate: Optional[float]
    counter_offer: Optional[float]
    outcome: Optional[str] = None


@dataclass
class CallRecord:
    load_id: Optional[str]
    mc_number: str
    outcome: CallOutcome
    sentiment: Sentiment
    agreed_rate: Optional[float]
    num_negotiations: int
    duration_seconds: Optional[int] = None
    id: Optional[int] = None
