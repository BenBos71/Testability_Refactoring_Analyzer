"""OOP Design Pattern Example

This file demonstrates a small object-oriented design with interfaces and
pluggable strategies.

Expected Score: Not range-targeted (real-world pattern example)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class TaxStrategy(Protocol):
    def compute_tax(self, subtotal: float) -> float: ...


@dataclass(frozen=True)
class NoTax:
    def compute_tax(self, subtotal: float) -> float:
        return 0.0


@dataclass(frozen=True)
class FlatRateTax:
    rate: float

    def compute_tax(self, subtotal: float) -> float:
        if subtotal <= 0:
            return 0.0
        return subtotal * self.rate


@dataclass(frozen=True)
class LineItem:
    sku: str
    unit_price: float
    quantity: int


class Invoice:
    def __init__(self, items: list[LineItem], tax: TaxStrategy):
        self._items = list(items)
        self._tax = tax

    def subtotal(self) -> float:
        return sum(item.unit_price * item.quantity for item in self._items)

    def total(self) -> float:
        subtotal = self.subtotal()
        return subtotal + self._tax.compute_tax(subtotal)
