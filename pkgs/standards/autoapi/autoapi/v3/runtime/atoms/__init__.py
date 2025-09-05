# autoapi/v3/runtime/atoms/__init__.py
from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Tuple

from .. import events as _ev

# Domain registries
from .emit import REGISTRY as _EMIT
from .out import REGISTRY as _OUT
from .refresh import REGISTRY as _REFRESH
from .resolve import REGISTRY as _RESOLVE
from .schema import REGISTRY as _SCHEMA
from .storage import REGISTRY as _STORAGE
from .wire import REGISTRY as _WIRE
from .response import REGISTRY as _RESPONSE

# Runner signature: (obj|None, ctx) -> None
RunFn = Callable[[Optional[object], Any], None]

#: Global registry consumed by runtime.plan:
#:   { (domain, subject): (anchor, runner) }
REGISTRY: Dict[Tuple[str, str], Tuple[str, RunFn]] = {}


def _add_bulk(source: Dict[Tuple[str, str], Tuple[str, RunFn]]) -> None:
    for key, val in source.items():
        if key in REGISTRY:
            raise RuntimeError(f"Duplicate atom registration: {key!r}")
        anchor, fn = val
        if not _ev.is_valid_event(anchor):
            raise ValueError(f"Atom {key!r} declares unknown anchor {anchor!r}")
        REGISTRY[key] = (anchor, fn)


# Aggregate all domains
_add_bulk(_EMIT)
_add_bulk(_OUT)
_add_bulk(_REFRESH)
_add_bulk(_RESOLVE)
_add_bulk(_SCHEMA)
_add_bulk(_STORAGE)
_add_bulk(_WIRE)
_add_bulk(_RESPONSE)

# ── Back-compat subject aliases (optional) ────────────────────────────────────
# Allow "wire:validate" as an alias of "wire:validate_in".
if ("wire", "validate_in") in REGISTRY and ("wire", "validate") not in REGISTRY:
    REGISTRY[("wire", "validate")] = REGISTRY[("wire", "validate_in")]

# ── Public helpers ────────────────────────────────────────────────────────────


def domains() -> Tuple[str, ...]:
    """Return all domains present in the registry."""
    return tuple(sorted({d for (d, _) in REGISTRY.keys()}))


def subjects(domain: str) -> Tuple[str, ...]:
    """Return subjects available for a given domain."""
    return tuple(sorted(s for (d, s) in REGISTRY.keys() if d == domain))


def get(domain: str, subject: str) -> Tuple[str, RunFn]:
    """Return (anchor, runner) for a given (domain, subject)."""
    key = (domain, subject)
    if key not in REGISTRY:
        raise KeyError(f"Unknown atom: {domain}:{subject}")
    return REGISTRY[key]


def all_items() -> Tuple[Tuple[Tuple[str, str], Tuple[str, RunFn]], ...]:
    """Return the registry items as a sorted tuple for deterministic iteration."""
    return tuple(sorted(REGISTRY.items(), key=lambda kv: (kv[0][0], kv[0][1])))


__all__ = [
    "RunFn",
    "REGISTRY",
    "domains",
    "subjects",
    "get",
    "all_items",
]
