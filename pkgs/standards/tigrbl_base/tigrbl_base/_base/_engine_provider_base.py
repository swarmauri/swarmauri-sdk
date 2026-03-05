from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class EngineProviderBase(Protocol):
    """Provider-like runtime contract for engine provider objects."""

    spec: Any

    def to_provider(self) -> "EngineProviderBase": ...


__all__ = ["EngineProviderBase"]
