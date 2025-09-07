"""Helpers for collecting ctx-only hooks."""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, Iterable, Union

from ..runtime.executor import _Ctx
from ..op.collect import apply_alias
from ..op.mro_collect import mro_alias_map_for
from ..op.decorators import _maybe_await, _unwrap
from .decorators import HOOK_DECLS_ATTR, Hook

logger = logging.getLogger("uvicorn")


def _phase_io_key(phase: str) -> str | None:
    p = str(phase)
    if p.startswith("PRE_"):
        return "payload"
    if p.startswith("POST_"):
        return "result"
    if p.startswith("ON_"):
        return "error"
    return None


def _wrap_ctx_hook(
    table: type, func: Callable[..., Any], phase: str
) -> Callable[..., Any]:
    io_key = _phase_io_key(phase)

    async def hook(
        value=None, *, db=None, request=None, ctx: Dict[str, Any] | None = None
    ):
        ctx = _Ctx.ensure(request=request, db=db, seed=ctx)
        if io_key is not None and value is not None:
            ctx[io_key] = value
        bound = func.__get__(table, table)
        _ = await _maybe_await(bound(ctx))
        if io_key is None:
            return None
        return ctx.get(io_key, value)

    hook.__name__ = getattr(func, "__name__", "hook")
    hook.__qualname__ = getattr(func, "__qualname__", hook.__name__)
    return hook


def collect_decorated_hooks(
    table: type, *, visible_aliases: set[str]
) -> Dict[str, Dict[str, list[Callable[..., Any]]]]:
    """Build alias→phase→[hook] map from ctx-only hook declarations."""

    logger.info("Collecting hooks for %s", table.__name__)
    mapping: Dict[str, Dict[str, list[Callable[..., Any]]]] = {}
    aliases = mro_alias_map_for(table)

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
    logger.debug("Collected hooks for aliases: %s", list(mapping.keys()))
    return mapping


__all__ = ["collect_decorated_hooks"]
