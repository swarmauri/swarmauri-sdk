# autoapi/v3/runtime/atoms/refresh/__init__.py
from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Tuple

# Atom implementations (model-scoped)
from . import demand as _demand

# Runner signature: (obj|None, ctx) -> None
RunFn = Callable[[Optional[object], Any], None]

#: Domain-scoped registry consumed by runtime.plan (and aggregated at atoms/__init__.py).
#: Keys are (domain, subject); values are (anchor, runner).
REGISTRY: Dict[Tuple[str, str], Tuple[str, RunFn]] = {
    ("refresh", "demand"): (_demand.ANCHOR, _demand.run),
}


def subjects() -> Tuple[str, ...]:
    """Return the subject names exported by this domain."""
    return tuple(s for (_, s) in REGISTRY.keys())


def get(subject: str) -> Tuple[str, RunFn]:
    """Return (anchor, runner) for a subject in the 'refresh' domain."""
    key = ("refresh", subject)
    if key not in REGISTRY:
        raise KeyError(f"Unknown refresh atom subject: {subject!r}")
    return REGISTRY[key]


__all__ = ["REGISTRY", "RunFn", "subjects", "get"]
