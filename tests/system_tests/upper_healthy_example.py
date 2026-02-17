"""Upper Healthy Example - Testability Score: 90-100

This file demonstrates strong testability with only a small, intentional issue
so it should score in the upper end of the Healthy band, but not a perfect 100.

Expected Score: 90-100
Expected Classification: Healthy
Expected Violations: A small number of non-red-flag violations (e.g. parameter
count)
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Address:
    name: str
    line1: str
    city: str
    region: str
    postal_code: str
    country_code: str


def normalize_zip_code(postal_code: str) -> str:
    """Normalize a postal code for consistent output."""
    return postal_code.strip().upper().replace(" ", "")


def build_shipping_label(
    recipient_name: str,
    street_line1: str,
    city: str,
    region: str,
    postal_code: str,
    country_code: str,
) -> str:
    """Build a shipping label.

    Intentionally uses 6 parameters (threshold is 5) to trigger a small, non-
    red-flag penalty while keeping the implementation simple and testable.
    """
    normalized_postal = normalize_zip_code(postal_code)
    normalized_country = country_code.strip().upper()

    return "\n".join(
        [
            recipient_name.strip(),
            street_line1.strip(),
            f"{city.strip()}, {region.strip()} {normalized_postal}",
            normalized_country,
        ]
    )


def build_label_from_address(address: Address) -> str:
    """Convenience wrapper for building a label from an Address object."""
    return build_shipping_label(
        recipient_name=address.name,
        street_line1=address.line1,
        city=address.city,
        region=address.region,
        postal_code=address.postal_code,
        country_code=address.country_code,
    )
