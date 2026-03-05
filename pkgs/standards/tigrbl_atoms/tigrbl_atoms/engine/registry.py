from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Optional, Tuple, Dict


# A registration for an engine kind provided by an external (or built-in) package.
@dataclass
class EngineRegistration:
    build: Callable[..., Tuple[Any, Callable[[], Any]]]
    capabilities: Optional[Callable[[], Any]] = None


_registry: Dict[str, EngineRegistration] = {}


def register_engine(
    kind: str,
    build: Callable[..., Tuple[Any, Callable[[], Any]]],
    capabilities: Optional[Callable[[], Any]] = None,
) -> None:
    """Register an engine kind → (builder, capabilities). Idempotent."""
    k = (kind or "").strip().lower()
    if not k:
        raise ValueError("engine kind must be a non-empty string")
    if k in _registry:
        # idempotent registration
        return
    _registry[k] = EngineRegistration(build=build, capabilities=capabilities)


def get_engine_registration(kind: str) -> Optional[EngineRegistration]:
    return _registry.get((kind or "").strip().lower())


def known_engine_kinds() -> list[str]:
    return sorted(_registry.keys())
