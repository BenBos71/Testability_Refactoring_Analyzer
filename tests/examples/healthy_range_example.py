"""Healthy Range Example - Testability Score: 76-100

This file demonstrates generally good testability with a small amount of
complexity that should result in a score within the Healthy band, but not a
perfect 100.

Expected Score: 76-100
Expected Classification: Healthy
Expected Violations: A small number of non-red-flag violations (e.g. branching,
parameter count)
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable


@dataclass(frozen=True)
class LineItem:
    sku: str
    unit_price: Decimal
    quantity: int


def calculate_subtotal(items: Iterable[LineItem]) -> Decimal:
    """Calculate the subtotal for a list of line items."""
    subtotal = Decimal("0")
    for item in items:
        subtotal += item.unit_price * Decimal(item.quantity)
    return subtotal


def calculate_invoice_total(
    items: Iterable[LineItem],
    tax_rate: Decimal,
    discount_rate: Decimal,
    shipping_cost: Decimal,
    coupon_code: str | None,
    loyalty_tier: str,
) -> Decimal:
    """Calculate a realistic invoice total.

    Intentionally includes a few branching cases and a higher parameter count
    so the analyzer should deduct some points while still staying in the
    Healthy range.
    """
    subtotal = calculate_subtotal(items)

    if subtotal <= 0:
        return Decimal("0")

    coupon_discounts = {
        "WELCOME10": Decimal("0.10"),
        "VIP20": Decimal("0.20"),
    }
    loyalty_discounts = {
        "gold": Decimal("0.05"),
        "platinum": Decimal("0.08"),
        "staff": Decimal("0.10"),
    }

    applied_discount_rate = discount_rate
    if coupon_code:
        coupon_discount = coupon_discounts.get(coupon_code)
        if coupon_discount is None and coupon_code.startswith("SEASON"):
            coupon_discount = Decimal("0.15")
        if coupon_discount is not None:
            applied_discount_rate = max(applied_discount_rate, coupon_discount)

    tier_discount = loyalty_discounts.get(loyalty_tier)
    if tier_discount is not None:
        applied_discount_rate = max(applied_discount_rate, tier_discount)

    if applied_discount_rate < 0:
        applied_discount_rate = Decimal("0")
    if applied_discount_rate > 1:
        applied_discount_rate = Decimal("1")

    discounted = subtotal * (Decimal("1") - applied_discount_rate)

    taxable_amount = discounted
    if shipping_cost > 0:
        taxable_amount += shipping_cost

    tax = taxable_amount * tax_rate

    total = discounted + shipping_cost + tax
    if total < 0:
        return Decimal("0")
    return total
