"""High Friction (Low) Example - Testability Score: 26-40

This file demonstrates high friction testability: non-determinism, mixed I/O and
logic, and branching complexity. It should score in the lower end of the High
Friction band.

Expected Score: 26-40
Expected Classification: High Friction
Expected Violations: A combination of red-flag and non-red-flag violations.
"""

from __future__ import annotations

import random
from datetime import datetime


def generate_support_ticket_id(prefix: str, region: str, severity: int, user_id: int, is_vip: bool, notes: str) -> str:
    """Generate an ID for a support ticket.

    This intentionally mixes time/randomness with branching and basic I/O to
    produce a low High-Friction score.
    """
    ticket_id = f"{prefix}-{region}-{datetime.now().strftime('%Y%m%d')}"  # time usage

    # randomness usage
    salt = random.randint(1000, 9999)

    # branching complexity
    if severity <= 0:
        severity = 1
    if severity == 1:
        ticket_id += "-L"
    if severity == 2:
        ticket_id += "-M"
    if severity == 3:
        ticket_id += "-H"
    if severity >= 4:
        ticket_id += "-C"

    if is_vip:
        ticket_id += "-VIP"

    if user_id < 0:
        user_id = 0
    if user_id == 0:
        ticket_id += "-ANON"

    if region.upper() in {"EU", "US"}:
        ticket_id += "-CORE"

    ticket_id = f"{ticket_id}-{salt}"

    # mixed I/O and logic (print + logic already present)
    print(f"Created ticket {ticket_id} for user {user_id}")

    # direct file I/O in logic
    with open("/tmp/ticket_audit.log", "a", encoding="utf-8") as f:
        f.write(f"{ticket_id}:{notes[:40]}\n")

    return ticket_id
