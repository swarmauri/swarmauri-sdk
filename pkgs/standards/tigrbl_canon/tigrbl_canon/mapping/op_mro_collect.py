from __future__ import annotations

from functools import lru_cache
from typing import Dict

from tigrbl_core._spec import OpSpec


def _merge_mro_dict(cls: type, attr: str) -> Dict[str, str]:
    merged: Dict[str, str] = {}
    for base in reversed(cls.__mro__):
        merged.update(getattr(base, attr, {}) or {})
    return merged


@lru_cache(maxsize=None)
def mro_alias_map_for(table: type) -> Dict[str, str]:
    """Collect alias overrides across the model MRO."""
    return _merge_mro_dict(table, "__tigrbl_aliases__")


@lru_cache(maxsize=None)
def mro_collect_decorated_ops(table: type) -> list[OpSpec]:
    """Collect ctx-decorated ops if present on the model MRO."""
    out: list[OpSpec] = []
    seen: set[str] = set()
    for base in table.__mro__:
        for name, value in vars(base).items():
            if name in seen:
                continue
            fn = getattr(value, "__func__", value)
            spec = getattr(fn, "__tigrbl_op_spec__", None) or getattr(
                fn, "__tigrbl_op_decl__", None
            )
            if isinstance(spec, OpSpec):
                out.append(spec)
                seen.add(name)
    return out


__all__ = ["mro_alias_map_for", "mro_collect_decorated_ops"]
