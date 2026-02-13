"""High Friction (High) Example - Testability Score: 41-50

This file demonstrates high friction testability, but not as severe as the low
High Friction example. It includes non-determinism and some branching that
should land it in the upper end of the High Friction band.

Expected Score: 41-50
Expected Classification: High Friction
Expected Violations: A combination of red-flag and non-red-flag violations.
"""

from __future__ import annotations

import random
from datetime import datetime


def calculate_dynamic_discount(customer_tier: str, cart_total: float, is_first_order: bool, region: str, experiment_bucket: str, coupon_code: str | None) -> float:
    """Calculate a discount percentage.

    Intentionally includes a small amount of non-determinism and branching plus
    mixed I/O to land in the 41-50 range.
    """
    base = 0.0

    if customer_tier == "gold":
        base += 0.03
    if customer_tier == "platinum":
        base += 0.05

    if is_first_order:
        base += 0.02

    if cart_total > 200:
        base += 0.01
    if cart_total > 1000:
        base += 0.02

    if region.upper() in {"EU", "CA"}:
        base += 0.01

    if coupon_code == "WELCOME10":
        base = max(base, 0.10)

    # time + randomness red flags
    if datetime.now().hour < 6:
        base += 0.01
    base += (random.random() - 0.5) * 0.01

    # mixed I/O and logic
    print(f"bucket={experiment_bucket} discount={base:.4f}")

    # direct file I/O in logic (intentional testability penalty)
    with open("/tmp/discount_audit.log", "a", encoding="utf-8") as f:
        f.write(f"{experiment_bucket}:{base:.4f}\n")

    # clamp
    if base < 0:
        return 0.0
    if base > 0.30:
        return 0.30
    return base
