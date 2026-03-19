"""Engine provider registry used by :mod:`tigrbl_core._spec.engine_spec`."""

from __future__ import annotations

from typing import Any, Protocol


class EngineRegistration(Protocol):
    """Shape expected by :class:`EngineSpec` for engine providers."""

    def build(self, *, mapping: dict[str, object], spec: Any, dsn: str | None) -> Any:
        """Return a tuple of (engine, sessionmaker/session factory)."""

    def capabilities(
        self, *, spec: Any, mapping: dict[str, object] | None = None
    ) -> dict[str, Any]:
        """Return capability metadata for the engine implementation."""


_ENGINE_REGISTRY: dict[str, EngineRegistration] = {}


def register_engine(kind: str, registration: EngineRegistration) -> None:
    """Register an engine provider implementation by ``kind``."""
    key = (kind or "").strip().lower()
    if not key:
        raise ValueError("Engine kind must be a non-empty string")
    _ENGINE_REGISTRY[key] = registration


def get_engine_registration(kind: str) -> EngineRegistration | None:
    """Return the provider registration for ``kind`` if present."""
    return _ENGINE_REGISTRY.get((kind or "").strip().lower())


def known_engine_kinds() -> tuple[str, ...]:
    """Return all registered engine kinds in deterministic order."""
    return tuple(sorted(_ENGINE_REGISTRY))
