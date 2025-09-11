# tigrbl/v3/runtime/atoms/schema/__init__.py
from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Tuple
import logging

# Atom implementations (model-scoped)
from . import collect_in as _collect_in
from . import collect_out as _collect_out

# Runner signature: (obj|None, ctx) -> None
RunFn = Callable[[Optional[object], Any], None]

#: Domain-scoped registry consumed by the kernel plan (and aggregated at atoms/__init__.py).
#: Keys are (domain, subject); values are (anchor, runner).
REGISTRY: Dict[Tuple[str, str], Tuple[str, RunFn]] = {
    ("schema", "collect_in"): (_collect_in.ANCHOR, _collect_in.run),
    ("schema", "collect_out"): (_collect_out.ANCHOR, _collect_out.run),
}

logger = logging.getLogger("uvicorn")


def subjects() -> Tuple[str, ...]:
    """Return the subject names exported by this domain."""
    subjects = tuple(s for (_, s) in REGISTRY.keys())
    logger.debug("Listing 'schema' subjects: %s", subjects)
    return subjects


def get(subject: str) -> Tuple[str, RunFn]:
    """Return (anchor, runner) for a subject in the 'schema' domain."""
    key = ("schema", subject)
    if key not in REGISTRY:
        raise KeyError(f"Unknown schema atom subject: {subject!r}")
    logger.debug("Retrieving 'schema' subject %s", subject)
    return REGISTRY[key]


__all__ = ["REGISTRY", "RunFn", "subjects", "get"]
