from __future__ import annotations

from typing import Dict, Iterable

from .types import OpSpec


def apply_alias(verb: str, alias_map: Dict[str, str]) -> str:
    """Resolve canonical verb → alias (falls back to verb)."""
    return alias_map.get(verb, verb)


def _is_bound(model: type) -> bool:
    ops = getattr(model, "ops", None)
    all_specs = getattr(ops, "all", None)
    return isinstance(all_specs, tuple)


def _ensure_auto_bound(model: type) -> None:
    if _is_bound(model):
        return
    from ..bindings.model import bind

    bind(model)


def collect_specs(model: type, *, auto_bind: bool = True) -> Iterable[OpSpec]:
    """Collect resolved specs from the bound model view.

    When auto_bind is enabled (default), this guarantees the model has been
    bound before reading `model.ops.all`.
    """
    if auto_bind:
        _ensure_auto_bound(model)
        return tuple(getattr(getattr(model, "ops", None), "all", ()) or ())

    from .resolver import _resolve_unbound

    return tuple(_resolve_unbound(model))


def collect_alias_map(model: type, *, auto_bind: bool = True) -> Dict[str, str]:
    """Collect canonical-op alias mapping with auto-binding by default."""
    if auto_bind:
        _ensure_auto_bound(model)
        alias_map = getattr(model, "alias_map", None)
        if isinstance(alias_map, dict):
            return dict(alias_map)

    from .mro_collect import _collect_alias_map_unbound

    return _collect_alias_map_unbound(model)


__all__ = ["apply_alias", "collect_specs", "collect_alias_map"]
