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
from ..status import create_standardized_error, to_rpc_error_payload

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
    temp = getattr(ctx, "temp", None)
    if isinstance(temp, dict) and temp.get("rpc_short_circuit"):
        if phase not in {"EGRESS_SHAPE", "EGRESS_FINALIZE", "POST_RESPONSE"}:
            return

    if not chain:
        return

    for idx, step in enumerate(chain):
        label = getattr(step, "__tigrbl_label", None)
        if not isinstance(label, str) or not label:
            label = f"phase:{phase}:step:{idx}"

        seq = _trace.start(ctx, label) if _trace is not None else None
        try:
            rv = step(ctx)
            rv = await _maybe_await(rv)
            if rv is not None:
                ctx.result = rv
            if _trace is not None:
                _trace.end(ctx, seq, status=_trace.OK)
        except Exception as exc:
            temp = getattr(ctx, "temp", None)
            route = temp.get("route") if isinstance(temp, dict) else None
            rpc_env = route.get("rpc_envelope") if isinstance(route, dict) else None
            if isinstance(rpc_env, dict) and rpc_env.get("jsonrpc") == "2.0":
                std_exc = create_standardized_error(exc)
                ctx.status_code = 200
                ctx.result = None
                if isinstance(temp, dict):
                    temp["rpc_short_circuit"] = True
                    temp["rpc_error"] = to_rpc_error_payload(std_exc)
                if _trace is not None:
                    _trace.attach_error(ctx, seq, exc)
                    _trace.end(ctx, seq, status=_trace.ERROR)
                return
            if _trace is not None:
                _trace.attach_error(ctx, seq, exc)
                _trace.end(ctx, seq, status=_trace.ERROR)
            raise


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
