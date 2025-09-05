# autoapi/v3/hook/collect.py
from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, Union

from . import HOOK_DECLS_ATTR, Hook
from ..op.decorators import alias_map_for, apply_alias, _unwrap, _wrap_ctx_hook


def collect_decorated_hooks(
    table: type,
    *,
    visible_aliases: set[str],
) -> Dict[str, Dict[str, list[Callable[..., Any]]]]:
    """Build alias→phase→[hook] map from ctx-only hook declarations."""

    mapping: Dict[str, Dict[str, list[Callable[..., Any]]]] = {}
    aliases = alias_map_for(table)

    def _resolve_ops(spec: Union[str, Iterable[str]]) -> Iterable[str]:
        if spec == "*":
            return visible_aliases
        if isinstance(spec, str):
            return [spec if spec in visible_aliases else apply_alias(spec, aliases)]
        out: list[str] = []
        for x in spec:
            out.append(x if x in visible_aliases else apply_alias(x, aliases))
        return out

    for base in reversed(table.__mro__):
        for name in dir(base):
            attr = getattr(base, name, None)
            func = _unwrap(attr)
            decls: list[Hook] | None = getattr(func, HOOK_DECLS_ATTR, None)
            if not decls:
                continue
            for d in decls:
                for op in _resolve_ops(d.ops):
                    if op not in visible_aliases:
                        continue
                    ph = d.phase
                    mapping.setdefault(op, {}).setdefault(ph, []).append(
                        _wrap_ctx_hook(table, d.fn, ph)
                    )
    return mapping


__all__ = ["collect_decorated_hooks"]
