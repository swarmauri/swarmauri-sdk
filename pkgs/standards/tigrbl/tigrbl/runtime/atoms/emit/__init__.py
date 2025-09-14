# tigrbl/v3/runtime/atoms/emit/__init__.py
from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Tuple
import logging

# Atom implementations (model-scoped)
from . import paired_pre as _paired_pre
from . import paired_post as _paired_post
from . import readtime_alias as _readtime_alias

# Runner signature: (obj|None, ctx) -> None
RunFn = Callable[[Optional[object], Any], None]

#: Domain-scoped registry consumed by the kernel plan (and aggregated at atoms/__init__.py).
#: Keys are (domain, subject); values are (anchor, runner).
REGISTRY: Dict[Tuple[str, str], Tuple[str, RunFn]] = {
    ("emit", "paired_pre"): (_paired_pre.ANCHOR, _paired_pre.run),
    ("emit", "paired_post"): (_paired_post.ANCHOR, _paired_post.run),
    ("emit", "readtime_alias"): (_readtime_alias.ANCHOR, _readtime_alias.run),
}

logger = logging.getLogger("uvicorn")


def subjects() -> Tuple[str, ...]:
    """Return the subject names exported by this domain."""
    subjects = tuple(s for (_, s) in REGISTRY.keys())
    logger.debug("Listing 'emit' subjects: %s", subjects)
    return subjects


def get(subject: str) -> Tuple[str, RunFn]:
    """Return (anchor, runner) for a subject in the 'emit' domain."""
    key = ("emit", subject)
    if key not in REGISTRY:
        raise KeyError(f"Unknown emit atom subject: {subject!r}")
    logger.debug("Retrieving 'emit' subject %s", subject)
    return REGISTRY[key]


__all__ = ["REGISTRY", "RunFn", "subjects", "get"]
