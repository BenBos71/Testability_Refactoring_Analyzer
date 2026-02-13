"""Caution (Low) Example - Testability Score: 51-65

This file demonstrates code that is still understandable, but contains enough
branching complexity (and a small parameter-count issue) that it should score
in the low end of the Caution band.

Expected Score: 51-65
Expected Classification: Caution
Expected Violations: Non-red-flag violations (primarily Branch Explosion Risk,
plus Excessive Parameter Count)
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CustomerSnapshot:
    tenure_months: int
    late_payments_last_year: int
    chargebacks_last_year: int
    avg_monthly_spend: float
    has_verified_identity: bool


def compute_manual_review_score(
    snapshot: CustomerSnapshot,
    country_code: str,
    payment_method: str,
    is_first_order: bool,
    cart_total: float,
    device_trust_score: int,
) -> int:
    """Compute a manual-review score (0-100).

    Intentionally uses a higher parameter count and a long series of branching
    checks to demonstrate a "Caution" score.
    """
    score = 0

    if snapshot.tenure_months < 1:
        score += 8
    if snapshot.tenure_months < 6:
        score += 4
    if snapshot.late_payments_last_year > 0:
        score += 6
    if snapshot.late_payments_last_year > 2:
        score += 6
    if snapshot.chargebacks_last_year > 0:
        score += 10
    if snapshot.chargebacks_last_year > 1:
        score += 10
    if snapshot.avg_monthly_spend < 20:
        score += 6
    if snapshot.avg_monthly_spend > 1000:
        score += 4
    if not snapshot.has_verified_identity:
        score += 10

    if country_code.upper() in {"NG", "PK", "UA"}:
        score += 6
    if payment_method.lower() in {"wire", "crypto"}:
        score += 8
    if is_first_order:
        score += 6
    if cart_total > 500:
        score += 5
    if cart_total > 2000:
        score += 10

    if device_trust_score < 20:
        score += 10
    if device_trust_score < 50:
        score += 5
    if device_trust_score > 95:
        score -= 4

    if score < 0:
        score = 0
    if score > 100:
        score = 100

    return score
