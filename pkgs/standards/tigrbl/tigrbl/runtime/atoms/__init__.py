# tigrbl/v3/runtime/atoms/__init__.py
from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Tuple
import logging

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

#: Global registry consumed by the kernel plan:
#:   { (domain, subject): (anchor, runner) }
REGISTRY: Dict[Tuple[str, str], Tuple[str, RunFn]] = {}

logger = logging.getLogger("uvicorn")


def _add_bulk(source: Dict[Tuple[str, str], Tuple[str, RunFn]]) -> None:
    for key, val in source.items():
        if key in REGISTRY:
            logger.error("Duplicate atom registration attempted: %s", key)
            raise RuntimeError(f"Duplicate atom registration: {key!r}")
        anchor, fn = val
        if not _ev.is_valid_event(anchor):
            logger.error("Atom %s declares unknown anchor %s", key, anchor)
            raise ValueError(f"Atom {key!r} declares unknown anchor {anchor!r}")
        REGISTRY[key] = (anchor, fn)
        logger.debug("Registered atom %s -> %s", key, anchor)


# Aggregate all domains
_add_bulk(_EMIT)
_add_bulk(_OUT)
_add_bulk(_REFRESH)
_add_bulk(_RESOLVE)
_add_bulk(_SCHEMA)
_add_bulk(_STORAGE)
_add_bulk(_WIRE)
_add_bulk(_RESPONSE)

logger.info("Loaded %d runtime atoms", len(REGISTRY))

# ── Back-compat subject aliases (optional) ────────────────────────────────────
# Allow "wire:validate" as an alias of "wire:validate_in".
if ("wire", "validate_in") in REGISTRY and ("wire", "validate") not in REGISTRY:
    REGISTRY[("wire", "validate")] = REGISTRY[("wire", "validate_in")]

# ── Public helpers ────────────────────────────────────────────────────────────


def domains() -> Tuple[str, ...]:
    """Return all domains present in the registry."""
    out = tuple(sorted({d for (d, _) in REGISTRY.keys()}))
    logger.debug("Listing domains: %s", out)
    return out


def subjects(domain: str) -> Tuple[str, ...]:
    """Return subjects available for a given domain."""
    out = tuple(sorted(s for (d, s) in REGISTRY.keys() if d == domain))
    logger.debug("Listing subjects for %s: %s", domain, out)
    return out


def get(domain: str, subject: str) -> Tuple[str, RunFn]:
    """Return (anchor, runner) for a given (domain, subject)."""
    key = (domain, subject)
    if key not in REGISTRY:
        logger.error("Unknown atom requested: %s:%s", domain, subject)
        raise KeyError(f"Unknown atom: {domain}:{subject}")
    val = REGISTRY[key]
    logger.debug("Retrieved atom %s:%s -> %s", domain, subject, val[0])
    return val


def all_items() -> Tuple[Tuple[Tuple[str, str], Tuple[str, RunFn]], ...]:
    """Return the registry items as a sorted tuple for deterministic iteration."""
    items = tuple(sorted(REGISTRY.items(), key=lambda kv: (kv[0][0], kv[0][1])))
    logger.debug("Listing all registry items (%d)", len(items))
    return items


__all__ = [
    "RunFn",
    "REGISTRY",
    "domains",
    "subjects",
    "get",
    "all_items",
]
