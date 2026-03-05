# tigrbl/v3/runtime/atoms/wire/__init__.py
from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Tuple
import logging

# Atom implementations (per-field)
from . import build_in as _build_in
from . import validate_in as _validate_in
from . import build_out as _build_out
from . import dump as _dump

# Runner signature: (obj|None, ctx) -> None
RunFn = Callable[[Optional[object], Any], None]

#: Domain-scoped registry consumed by the kernel plan (and aggregated at atoms/__init__.py).
#: Keys are (domain, subject); values are (anchor, runner).
#: Canonical subjects mirror filenames; we keep "validate_in" (not "validate") to avoid duplicates.
REGISTRY: Dict[Tuple[str, str], Tuple[str, RunFn]] = {
    ("wire", "build_in"): (_build_in.ANCHOR, _build_in.run),
    ("wire", "validate_in"): (_validate_in.ANCHOR, _validate_in.run),
    ("wire", "build_out"): (_build_out.ANCHOR, _build_out.run),
    ("wire", "dump"): (_dump.ANCHOR, _dump.run),
}

logger = logging.getLogger("uvicorn")


def subjects() -> Tuple[str, ...]:
    """Return the subject names exported by this domain."""
    subjects = tuple(s for (_, s) in REGISTRY.keys())
    logger.debug("Listing 'wire' subjects: %s", subjects)
    return subjects


def get(subject: str) -> Tuple[str, RunFn]:
    """Return (anchor, runner) for a subject in the 'wire' domain."""
    key = ("wire", subject)
    if key not in REGISTRY:
        raise KeyError(f"Unknown wire atom subject: {subject!r}")
    logger.debug("Retrieving 'wire' subject %s", subject)
    return REGISTRY[key]


__all__ = ["REGISTRY", "RunFn", "subjects", "get"]
