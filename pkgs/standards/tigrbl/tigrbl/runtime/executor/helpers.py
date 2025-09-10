# tigrbl/v3/runtime/executor/helpers.py
from __future__ import annotations

import inspect
import logging
from typing import Any, Iterable, Optional, Sequence

try:
    from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore
except Exception:  # pragma: no cover
    AsyncSession = Any  # type: ignore

try:
    from .. import trace as _trace  # type: ignore
except Exception:  # pragma: no cover
    _trace = None  # type: ignore

from .types import _Ctx, HandlerStep, PhaseChains

logger = logging.getLogger(__name__)


def _is_async_db(db: Any) -> bool:
    """Detect DB interfaces that require `await` for transactional methods."""
    if isinstance(db, AsyncSession) or hasattr(db, "run_sync"):
        return True
    for attr in ("commit", "begin", "rollback", "flush"):
        if inspect.iscoroutinefunction(getattr(db, attr, None)):
            return True
    return False


def _bool_call(meth: Any) -> bool:
    try:
        return bool(meth())
    except Exception:  # pragma: no cover
        return False


def _in_tx(db: Any) -> bool:
    for name in ("in_transaction", "in_nested_transaction"):
        attr = getattr(db, name, None)
        if callable(attr):
            if _bool_call(attr):
                return True
        elif attr:
            return True
    return False


async def _maybe_await(v: Any) -> Any:
    if inspect.isawaitable(v):
        return await v  # type: ignore[func-returns-value]
    return v


async def _run_chain(
    ctx: _Ctx, chain: Optional[Iterable[HandlerStep]], *, phase: str
) -> None:
    if not chain:
        return
    if _trace is not None:
        with _trace.span(ctx, f"phase:{phase}"):
            for step in chain:
                rv = step(ctx)
                rv = await _maybe_await(rv)
                if rv is not None:
                    ctx.result = rv
        return
    for step in chain:
        rv = step(ctx)
        rv = await _maybe_await(rv)
        if rv is not None:
            ctx.result = rv


def _g(phases: Optional[PhaseChains], key: str) -> Sequence[HandlerStep]:
    return () if not phases else phases.get(key, ())


__all__ = [
    "_is_async_db",
    "_bool_call",
    "_in_tx",
    "_maybe_await",
    "_run_chain",
    "_g",
]
