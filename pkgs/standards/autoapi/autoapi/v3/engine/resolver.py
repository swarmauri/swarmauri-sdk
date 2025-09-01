# autoapi/autoapi/v3/engine/resolver.py
from __future__ import annotations

import asyncio
import inspect
import threading
from typing import Any, Callable, Optional

from ._engine import AsyncSession, Engine, Provider, Session
from .engine_spec import EngineSpec, EngineCfg

# Registry with strict precedence: op > model > api > app
_LOCK = threading.RLock()
_DEFAULT: Optional[Provider] = None
_API: dict[int, Provider] = {}
_TAB: dict[Any, Provider] = {}
_OP: dict[tuple[Any, str], Provider] = {}


def _coerce(ctx: Optional[EngineCfg]) -> Optional[Provider]:
    """
    Promote an @engine_ctx value to a lazy Provider.
    """
    if ctx is None:
        return None
    if isinstance(ctx, Provider):
        return ctx
    if isinstance(ctx, Engine):
        return ctx.provider
    if isinstance(ctx, EngineSpec):
        return ctx.to_provider()
    spec = EngineSpec.from_any(ctx)
    return spec.to_provider() if spec else None


# ---- registration -----------------------------------------------------------


def set_default(ctx: EngineCfg | None) -> None:
    """
    Register the app-level default Provider used when no API/table/op binds.
    """
    global _DEFAULT
    prov = _coerce(ctx)
    with _LOCK:
        _DEFAULT = prov


def register_api(api: Any, ctx: EngineCfg | None) -> None:
    """
    Register an API-level Provider.
    """
    prov = _coerce(ctx)
    if prov is None:
        return
    with _LOCK:
        _API[id(api)] = prov


def register_table(model: Any, ctx: EngineCfg | None) -> None:
    """
    Register a table/model-level Provider.
    """
    prov = _coerce(ctx)
    if prov is None:
        return
    with _LOCK:
        _TAB[model] = prov


def register_op(model: Any, alias: str, ctx: EngineCfg | None) -> None:
    """
    Register an op-level Provider for (model, alias).
    """
    prov = _coerce(ctx)
    if prov is None:
        return
    with _LOCK:
        _OP[(model, alias)] = prov


# ---- resolution -------------------------------------------------------------


def resolve_provider(
    *,
    api: Any = None,
    model: Any = None,
    op_alias: str | None = None,
) -> Optional[Provider]:
    """
    Resolve the effective Provider using precedence:
        op > model > api > app(default)
    """
    with _LOCK:
        if model is not None and op_alias is not None:
            p = _OP.get((model, op_alias))
            if p:
                return p
        if model is not None:
            p = _TAB.get(model)
            if p:
                return p
        if api is not None:
            p = _API.get(id(api))
            if p:
                return p
        return _DEFAULT


SessionT = Session | AsyncSession


def acquire(
    *,
    api: Any = None,
    model: Any = None,
    op_alias: str | None = None,
) -> tuple[SessionT, Callable[[], None]]:
    """
    Acquire a DB session from the resolved Provider.

    Returns:
        (session, release_fn)

    Raises:
        RuntimeError: if no Provider can be resolved and no default is set.
    """
    p = resolve_provider(api=api, model=model, op_alias=op_alias)
    if p is None:
        raise RuntimeError(
            f"No database provider configured for op={op_alias} "
            f"model={getattr(model, '__name__', model)} "
            f"api={type(api).__name__ if api else None} and no default"
        )
    db: SessionT = p.session()

    def _release() -> None:
        close = getattr(db, "close", None)
        if callable(close):
            try:
                rv = close()
                if inspect.isawaitable(rv):
                    try:
                        loop = asyncio.get_running_loop()
                    except RuntimeError:
                        asyncio.run(rv)
                    else:
                        loop.create_task(rv)
                # If close is sync, it has already executed
            except Exception:
                # best-effort close; swallow to avoid masking handler errors
                pass

    return db, _release
