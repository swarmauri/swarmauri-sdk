"""System step registry used by kernel plan compilation."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Callable

from .events import DEP_EXTRA, DEP_SECURITY
from .status import SystemStepError

START_TX = "START_TX"
HANDLER = "HANDLER"
END_TX = "END_TX"

INSTALLED = SimpleNamespace(begin=None, handler=None, commit=None, rollback=None)


def _ensure_temp(ctx: Any) -> dict[str, Any]:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    return temp


def _call_maybe_async(fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    rv = fn(*args, **kwargs)
    if hasattr(rv, "__await__"):
        return rv
    return rv


async def _await_tx_begin(begin_result: Any, temp: dict[str, Any]) -> None:
    try:
        await begin_result
        temp["__sys_tx_open__"] = True
    except Exception as exc:
        raise SystemStepError("txn begin failed", cause=exc) from exc


async def _sys_tx_begin(_obj: object | None, ctx: Any) -> None:
    temp = _ensure_temp(ctx)
    begin = getattr(INSTALLED, "begin", None)
    if begin is None:
        temp["__sys_tx_open__"] = False
        return
    try:
        rv = begin(ctx)
        if hasattr(rv, "__await__"):
            await _await_tx_begin(rv, temp)
            return
        temp["__sys_tx_open__"] = True
    except Exception as exc:
        raise SystemStepError("txn begin failed", cause=exc) from exc


async def _sys_tx_commit(_obj: object | None, ctx: Any) -> None:
    temp = _ensure_temp(ctx)
    if not bool(temp.get("__sys_tx_open__")):
        temp["__sys_tx_open__"] = False
        return
    commit = getattr(INSTALLED, "commit", None)
    try:
        if commit is not None:
            rv = _call_maybe_async(commit, ctx)
            if hasattr(rv, "__await__"):
                await rv
    except Exception as exc:
        raise SystemStepError("txn commit failed", cause=exc) from exc
    finally:
        temp["__sys_tx_open__"] = False


def _resolve_handler(ctx: Any) -> Callable[[object | None, Any], Any] | None:
    installed = getattr(INSTALLED, "handler", None)
    if callable(installed):
        return installed

    temp = _ensure_temp(ctx)
    temp_handler = temp.get("handler")
    if callable(temp_handler):
        return temp_handler

    ctx_handler = getattr(ctx, "handler", None)
    if callable(ctx_handler):
        return ctx_handler

    model = getattr(ctx, "model", None)
    runtime = getattr(model, "runtime", None)
    runtime_handler = getattr(runtime, "handler", None)
    if callable(runtime_handler):
        return runtime_handler

    model_handler = getattr(model, "handler", None)
    if callable(model_handler):
        return model_handler

    return None


def _sys_handler_crud(obj: object | None, ctx: Any) -> Any:
    handler = _resolve_handler(ctx)
    if not callable(handler):
        raise SystemStepError("missing handler")
    try:
        return handler(obj, ctx)
    except Exception as exc:
        raise SystemStepError("handler failed", cause=exc) from exc


def run_rollback(ctx: Any, err: BaseException | None) -> None:
    rollback = getattr(INSTALLED, "rollback", None)
    try:
        if callable(rollback):
            rollback(ctx, err)
            return
        session = getattr(ctx, "session", None)
        rb = getattr(session, "rollback", None)
        if callable(rb):
            rb()
    except Exception:
        return


_REGISTRY = {
    ("txn", "begin"): (START_TX, _sys_tx_begin),
    ("handler", "crud"): (HANDLER, _sys_handler_crud),
    ("txn", "commit"): (END_TX, _sys_tx_commit),
    ("dep", "security"): ("PRE_TX_BEGIN", DEP_SECURITY),
    ("dep", "extra"): ("PRE_TX_BEGIN", DEP_EXTRA),
}


def get(domain: str, subject: str):
    try:
        return _REGISTRY[(domain, subject)]
    except KeyError as exc:
        raise KeyError(f"unknown system subject: {(domain, subject)!r}") from exc


def subjects():
    return tuple(_REGISTRY.keys())


__all__ = [
    "START_TX",
    "HANDLER",
    "END_TX",
    "INSTALLED",
    "_sys_tx_begin",
    "_sys_tx_commit",
    "_sys_handler_crud",
    "run_rollback",
    "get",
    "subjects",
]
