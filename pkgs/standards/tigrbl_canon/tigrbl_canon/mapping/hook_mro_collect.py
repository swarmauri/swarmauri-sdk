"""Helpers for collecting ctx-only hooks."""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any, Callable, Dict, Iterable, Union

from tigrbl_runtime.runtime.executor import _Ctx
from .._concrete._op import Op as OpSpec
from .op_mro_collect import mro_alias_map_for
from ..decorators.op import _maybe_await, _unwrap
from ..decorators.hook import HOOK_DECLS_ATTR, Hook

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
        if phase == "POST_RESPONSE":
            response = ctx.get("response")
            result_payload = ctx.get("result")
            if result_payload is None and response is not None:
                result_payload = getattr(response, "result", None)
            if result_payload is not None:
                ctx["result"] = result_payload
                if response is not None:
                    setattr(response, "result", result_payload)
                temp = ctx.get("temp")
                if isinstance(temp, dict):
                    egress = temp.get("egress")
                    if isinstance(egress, dict):
                        enveloped = egress.get("enveloped")
                        if isinstance(enveloped, dict) and "result" in enveloped:
                            enveloped["result"] = result_payload
                        transport = egress.get("transport_response")
                        if isinstance(transport, dict):
                            body = transport.get("body")
                            if isinstance(body, dict) and "result" in body:
                                body["result"] = result_payload
        if io_key is None:
            return None
        return ctx.get(io_key, value)

    hook.__name__ = getattr(func, "__name__", "hook")
    hook.__qualname__ = getattr(func, "__qualname__", hook.__name__)
    return hook


@lru_cache(maxsize=None)
def _mro_collect_decorated_hooks_cached(
    table: type, visible_aliases_fs: frozenset[str]
) -> Dict[str, Dict[str, list[Callable[..., Any]]]]:
    """Cached helper for :func:`mro_collect_decorated_hooks`."""

    visible_aliases = set(visible_aliases_fs)
    logger.info("Collecting hooks for %s", table.__name__)
    mapping: Dict[str, Dict[str, list[Callable[..., Any]]]] = {}
    aliases = mro_alias_map_for(table)

    def _resolve_ops(spec: Union[str, Iterable[str]]) -> Iterable[str]:
        if spec == "*":
            return visible_aliases
        if isinstance(spec, str):
            return [
                spec if spec in visible_aliases else OpSpec.apply_alias(spec, aliases)
            ]
        out: list[str] = []
        for x in spec:
            out.append(x if x in visible_aliases else OpSpec.apply_alias(x, aliases))
        return out

    for base in reversed(table.__mro__):
        for name, attr in base.__dict__.items():
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


def mro_collect_decorated_hooks(
    table: type, *, visible_aliases: set[str]
) -> Dict[str, Dict[str, list[Callable[..., Any]]]]:
    """Collect alias→phase→[hook] declarations across a table's MRO."""

    return _mro_collect_decorated_hooks_cached(table, frozenset(visible_aliases))


__all__ = ["mro_collect_decorated_hooks"]
