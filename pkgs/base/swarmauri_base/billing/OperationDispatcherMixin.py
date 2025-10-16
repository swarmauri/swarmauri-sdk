"""Shared helpers for billing mixin implementations."""

from __future__ import annotations

from typing import Any, Mapping, Optional

from pydantic import BaseModel, ConfigDict


class OperationDispatcherMixin(BaseModel):
    """Base class for mixins that validates common billing inputs."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    def _require_idempotency(self, key: Optional[str]) -> None:
        """Ensure that the provided idempotency key is a non-empty string."""

        if not key or not key.strip():
            raise ValueError("idempotency_key is required and must be non-empty.")


def extract_raw_payload(raw: Mapping[str, Any]) -> Mapping[str, Any] | Any:
    """Return the provider payload embedded in ``raw`` if present."""

    if "raw" in raw:
        return raw["raw"]
    return raw


__all__ = ["OperationDispatcherMixin", "extract_raw_payload"]
