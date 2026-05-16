from dataclasses import dataclass
from decimal import Decimal

from transactions.models import DeviceBlacklist, Transaction


@dataclass(frozen=True)
class RiskDecision:
    status: str
    risk_score: int
    reasons: list[str]


class RiskEngine:
    HIGH_AMOUNT_LIMIT = Decimal("10000.00")

    def evaluate(
        self,
        *,
        amount: Decimal,
        device_fingerprint: str,
        ip_address: str,
        user_agent: str,
    ) -> RiskDecision:
        reasons = []
        normalized_fingerprint = device_fingerprint.strip().lower()

        if amount > self.HIGH_AMOUNT_LIMIT:
            reasons.append("AMOUNT_ABOVE_LIMIT")

        if DeviceBlacklist.objects.filter(
            fingerprint=normalized_fingerprint,
            is_active=True,
        ).exists():
            reasons.append("BLACKLISTED_DEVICE")

        if reasons:
            return RiskDecision(
                status=Transaction.Status.REJECTED,
                risk_score=100 if "BLACKLISTED_DEVICE" in reasons else 90,
                reasons=reasons,
            )

        return RiskDecision(
            status=Transaction.Status.APPROVED,
            risk_score=10,
            reasons=["LOW_RISK"],
        )
