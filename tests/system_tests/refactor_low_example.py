"""Refactor First (Low) Example - Testability Score: 0-15

This file demonstrates code that should be refactored before adding features.
It intentionally combines multiple red-flag patterns (time/randomness, mixed I/O
and logic, exception-driven control flow, global state mutation) and excessive
branching.

Expected Score: 0-15
Expected Classification: Refactor First
Expected Violations: Multiple red-flag and non-red-flag violations.
"""

from __future__ import annotations

import random
from datetime import datetime


GLOBAL_COUNTER = 0


def process_legacy_batch(
    records: list[dict],
    mode: str,
    retries: int,
    region: str,
    allow_partial: bool,
    audit_tag: str,
) -> int:
    """Process a batch of records in a legacy style.

    Intentionally difficult to test.
    """
    global GLOBAL_COUNTER

    # time + randomness
    run_id = f"{audit_tag}-{datetime.now().isoformat()}-{random.randint(1, 999999)}"

    # mixed I/O and logic
    print(f"run_id={run_id} count={len(records)}")

    # global state mutation
    GLOBAL_COUNTER += len(records)

    processed = 0

    for rec in records:
        try:
            # lots of branching
            if mode == "fast":
                if rec.get("priority") == "high":
                    processed += 2
                elif rec.get("priority") == "medium":
                    processed += 1
                else:
                    processed += 0
            elif mode == "safe":
                if rec.get("status") == "new":
                    processed += 1
                elif rec.get("status") == "retry":
                    processed += 1
                elif rec.get("status") == "dead":
                    processed -= 1
                else:
                    processed += 0
            elif mode == "compat":
                if region.upper() in {"EU", "US"}:
                    processed += 1
                elif region.upper() in {"NG", "PK", "UA"}:
                    processed += 2
                else:
                    processed += 0
            else:
                if allow_partial:
                    processed += 0
                else:
                    raise ValueError("unsupported mode")

            if rec.get("amount", 0) > 1000:
                processed += 1
            if rec.get("amount", 0) > 5000:
                processed += 1

        except Exception:
            # exception-driven control flow
            if retries > 0:
                retries -= 1
                processed += 0
            else:
                processed -= 2

    # direct file I/O in logic
    with open("/tmp/legacy_batch.log", "a", encoding="utf-8") as f:
        f.write(f"{run_id}:{processed}\n")

    return processed
