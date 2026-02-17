"""Web API Pattern Example

This file demonstrates common API-layer patterns (request validation, parsing,
response building) without relying on external web frameworks.

Expected Score: Not range-targeted (real-world pattern example)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class HttpResponse:
    status_code: int
    body: dict[str, Any]


def _require_str(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or value.strip() == "":
        raise ValueError(f"Missing or invalid '{key}'")
    return value.strip()


def _require_int(payload: dict[str, Any], key: str, *, min_value: int = 0) -> int:
    value = payload.get(key)
    if not isinstance(value, int):
        raise ValueError(f"Missing or invalid '{key}'")
    if value < min_value:
        raise ValueError(f"'{key}' must be >= {min_value}")
    return value


def create_user_handler(request_json: dict[str, Any]) -> HttpResponse:
    """Pretend HTTP handler that validates input and returns a response."""
    try:
        name = _require_str(request_json, "name")
        email = _require_str(request_json, "email")
        age = _require_int(request_json, "age", min_value=13)
    except ValueError as exc:
        return HttpResponse(status_code=400, body={"error": str(exc)})

    user_id = f"usr_{name.lower().replace(' ', '_')}_{age}"

    return HttpResponse(
        status_code=201,
        body={
            "id": user_id,
            "name": name,
            "email": email,
        },
    )


def get_health_handler() -> HttpResponse:
    return HttpResponse(status_code=200, body={"status": "ok"})
