from __future__ import annotations

from typing import Any


class EngineBase:
    """Base contract for concrete engine façade implementations."""

    spec: Any

    def to_provider(self) -> Any:  # pragma: no cover - interface contract
        raise NotImplementedError


__all__ = ["EngineBase"]
