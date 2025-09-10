# tigrbl/v3/runtime/atoms/resolve/__init__.py
from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Tuple
import logging

# Atom implementations (model-scoped)
from . import assemble as _assemble
from . import paired_gen as _paired_gen

# Runner signature: (obj|None, ctx) -> None
RunFn = Callable[[Optional[object], Any], None]

#: Domain-scoped registry consumed by the kernel plan (and aggregated at atoms/__init__.py).
#: Keys are (domain, subject); values are (anchor, runner).
REGISTRY: Dict[Tuple[str, str], Tuple[str, RunFn]] = {
    ("resolve", "assemble"): (_assemble.ANCHOR, _assemble.run),
    ("resolve", "paired_gen"): (_paired_gen.ANCHOR, _paired_gen.run),
}

logger = logging.getLogger("uvicorn")


def subjects() -> Tuple[str, ...]:
    """Return the subject names exported by this domain."""
    subjects = tuple(s for (_, s) in REGISTRY.keys())
    logger.debug("Listing 'resolve' subjects: %s", subjects)
    return subjects


def get(subject: str) -> Tuple[str, RunFn]:
    """Return (anchor, runner) for a subject in the 'resolve' domain."""
    key = ("resolve", subject)
    if key not in REGISTRY:
        raise KeyError(f"Unknown resolve atom subject: {subject!r}")
    logger.debug("Retrieving 'resolve' subject %s", subject)
    return REGISTRY[key]


__all__ = ["REGISTRY", "RunFn", "subjects", "get"]
