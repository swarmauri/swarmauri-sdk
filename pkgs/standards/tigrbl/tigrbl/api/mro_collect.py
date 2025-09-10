# tigrbl/v3/api/mro_collect.py
from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any, Callable, Dict, Iterable, Mapping

from ..config.constants import TIGRBL_API_HOOKS_ATTR

logger = logging.getLogger("uvicorn")


@lru_cache(maxsize=None)
def mro_collect_api_hooks(api: type) -> Dict[str, Dict[str, list[Callable[..., Any]]]]:
    """Collect API-level hook declarations across ``api``'s MRO.

    The accepted shape mirrors the hooks mapping used by the bindings:
        {alias: {phase: Iterable[callable]}}
    Hooks from base classes are merged with subclass definitions taking precedence.
    """
    logger.info("Collecting API hooks for %s", api.__name__)
    out: Dict[str, Dict[str, list[Callable[..., Any]]]] = {}
    for base in reversed(api.__mro__):
        mapping = getattr(base, TIGRBL_API_HOOKS_ATTR, None)
        if not isinstance(mapping, Mapping):
            continue
        for alias, phase_map in mapping.items():
            bucket = out.setdefault(str(alias), {})
            if not isinstance(phase_map, Mapping):
                continue
            for phase, items in phase_map.items():
                lst = bucket.setdefault(str(phase), [])
                if isinstance(items, Iterable):
                    for fn in items:
                        if callable(fn):
                            lst.append(fn)
                elif callable(items):
                    lst.append(items)
    logger.debug("Collected API hooks for aliases: %s", list(out.keys()))
    return out


__all__ = ["mro_collect_api_hooks"]
