"""Utility helpers shared across billing mixins."""

from __future__ import annotations

from typing import Any, Mapping


def require_idempotency(key: str | None) -> None:
    """Ensure that an idempotency key is provided."""

    if key is None or not str(key).strip():
        raise ValueError("idempotency_key is required and must be non-empty.")


def extract_raw_payload(raw: Mapping[str, Any]) -> Mapping[str, Any] | Any:
    """Return the provider payload embedded in ``raw`` if present."""

    if "raw" in raw:
        return raw["raw"]
    return raw


__all__ = ["extract_raw_payload", "require_idempotency"]
