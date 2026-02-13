"""Data Processing Pattern Example

This file demonstrates a small data pipeline pattern: parsing input records,
transforming them, and aggregating summary statistics.

Expected Score: Not range-targeted (real-world pattern example)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Event:
    user_id: str
    event_type: str
    value: float


def parse_events(rows: Iterable[dict]) -> list[Event]:
    """Parse raw rows into typed Events."""
    events: list[Event] = []
    for row in rows:
        user_id = str(row.get("user_id", "")).strip()
        event_type = str(row.get("event_type", "")).strip()
        value = float(row.get("value", 0.0))

        if user_id == "" or event_type == "":
            continue

        events.append(Event(user_id=user_id, event_type=event_type, value=value))

    return events


def filter_events(events: Iterable[Event], allowed_types: set[str]) -> list[Event]:
    return [e for e in events if e.event_type in allowed_types]


def aggregate_by_user(events: Iterable[Event]) -> dict[str, float]:
    totals: dict[str, float] = {}
    for e in events:
        totals[e.user_id] = totals.get(e.user_id, 0.0) + e.value
    return totals


def top_users(totals: dict[str, float], *, limit: int = 5) -> list[tuple[str, float]]:
    return sorted(totals.items(), key=lambda kv: kv[1], reverse=True)[:limit]
