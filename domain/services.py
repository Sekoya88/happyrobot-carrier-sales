from domain.entities import NegotiationSession, NegotiationResult


class NegotiationService:
    def __init__(self, ceiling_pct: float = 0.05, max_rounds: int = 3):
        self.ceiling_pct = ceiling_pct
        self.max_rounds = max_rounds

    def evaluate_counter(
        self, session: NegotiationSession, counter_offer: float
    ) -> NegotiationResult:
        if session.round_count >= self.max_rounds:
            return NegotiationResult(
                accepted=False,
                agreed_rate=None,
                counter_offer=None,
                outcome="no_deal",
            )
        if counter_offer <= session.max_authorized_rate:
            return NegotiationResult(
                accepted=True,
                agreed_rate=counter_offer,
                counter_offer=None,
            )
        progressive = round(
            session.initial_rate
            + (session.max_authorized_rate - session.initial_rate)
            * (session.round_count + 1)
            / self.max_rounds,
            2,
        )
        return NegotiationResult(
            accepted=False,
            agreed_rate=None,
            counter_offer=progressive,
        )
