from __future__ import annotations

from typing import Dict


def apply_alias(verb: str, alias_map: Dict[str, str]) -> str:
    """Resolve canonical verb → alias (falls back to verb)."""
    return alias_map.get(verb, verb)


__all__ = ["apply_alias"]
