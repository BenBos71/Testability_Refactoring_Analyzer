"""Caution (High) Example - Testability Score: 66-75

This file demonstrates moderately testable code that still falls into the
"Caution" band. It intentionally includes some branching complexity and a
parameter-count issue, but is less complex than the low end caution example.

Expected Score: 66-75
Expected Classification: Caution
Expected Violations: Non-red-flag violations (primarily Branch Explosion Risk,
plus Excessive Parameter Count)
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OrderSignals:
    prior_orders: int
    refund_requests_last_year: int
    failed_payments_last_90_days: int
    account_age_days: int
    email_is_verified: bool


def compute_hold_probability_score(
    signals: OrderSignals,
    region_code: str,
    payment_method: str,
    cart_total: float,
    is_gift_order: bool,
    device_reputation_score: int,
) -> int:
    """Compute a hold probability score (0-100).

    Intentionally includes some branching beyond the analyzer threshold and a
    slightly excessive parameter count to land in the higher end of the Caution
    band.
    """
    score = 0

    if signals.account_age_days < 7:
        score += 8
    if signals.prior_orders == 0:
        score += 6
    if signals.failed_payments_last_90_days > 0:
        score += 8
    if signals.failed_payments_last_90_days > 2:
        score += 6
    if signals.refund_requests_last_year > 1:
        score += 8

    if not signals.email_is_verified:
        score += 6

    if region_code.upper() in {"BR", "AR", "TR"}:
        score += 6

    if payment_method.lower() in {"crypto", "wire"}:
        score += 8

    if cart_total > 1000:
        score += 8
    if cart_total > 3000:
        score += 8

    if is_gift_order:
        score += 4

    if device_reputation_score < 25:
        score += 10
    if device_reputation_score < 60:
        score += 4

    if score < 0:
        return 0
    if score > 100:
        return 100
    return score
