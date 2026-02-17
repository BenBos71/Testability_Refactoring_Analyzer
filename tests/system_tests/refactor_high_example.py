"""Refactor First (High) Example - Testability Score: 16-25

This file demonstrates code that is still in the "Refactor First" band, but not
as severe as the lowest example. It intentionally combines non-determinism with
mixed I/O/logic and branching to land in the upper part of the Refactor First
range.

Expected Score: 16-25
Expected Classification: Refactor First
Expected Violations: A few red-flag patterns plus branching complexity.
"""

from __future__ import annotations

import random
from datetime import datetime


cache: list[float] = []


def compute_unstable_rate(
    base_rate: float,
    customer_tier: str,
    cart_total: float,
    region: str,
    feature_flag: str,
    request_id: str,
) -> float:
    """Compute a rate in an intentionally hard-to-test way."""
    rate = base_rate

    # branching
    if customer_tier == "gold":
        rate += 0.01
    if customer_tier == "platinum":
        rate += 0.02

    if cart_total > 200:
        rate += 0.01
    if cart_total > 1000:
        rate += 0.02
    if cart_total > 2500:
        rate += 0.02

    if region.upper() in {"EU", "CA"}:
        rate += 0.01

    if feature_flag == "EXPERIMENT_A":
        rate += 0.01
    if feature_flag == "EXPERIMENT_B":
        rate += 0.015

    if feature_flag.startswith("ROLLOUT_"):
        rate += 0.005

    if customer_tier not in {"standard", "gold", "platinum"}:
        rate += 0.005

    # time + randomness
    if datetime.now().hour < 6:
        rate += 0.01
    rate += (random.random() - 0.5) * 0.02

    # mixed I/O and logic
    print(f"request_id={request_id} rate={rate:.4f}")

    # direct file I/O in logic
    with open("/tmp/rate_audit.log", "a", encoding="utf-8") as f:
        f.write(f"{request_id}:{rate:.4f}\n")

    # global state mutation (intentional red-flag penalty)
    cache.append(rate)

    # exception-driven control flow (intentional red-flag penalty)
    try:
        if request_id.strip() == "":
            raise ValueError("empty request_id")
    except ValueError:
        rate += 0.01

    if rate < 0:
        return 0.0
    if rate > 1.0:
        return 1.0
    return rate
