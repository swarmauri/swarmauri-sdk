"""Shared helpers for billing mixin implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping, Optional

from pydantic import BaseModel, ConfigDict

from swarmauri_core.billing import Operation


class OperationDispatcherMixin(BaseModel, ABC):
    """Base class for mixins that delegate operations to a provider."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    @abstractmethod
    def _op(
        self,
        operation: Operation,
        payload: Mapping[str, Any],
        *,
        idempotency_key: Optional[str] = None,
    ) -> Any:
        """Dispatch ``operation`` to the underlying provider implementation."""

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
