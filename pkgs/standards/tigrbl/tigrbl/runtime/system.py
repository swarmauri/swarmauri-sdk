# tigrbl/v3/runtime/system.py
from __future__ import annotations

import logging
import inspect
from typing import Any, Callable, Dict, Mapping, MutableMapping, Optional, Tuple

from . import errors as _err
from .executor.helpers import _in_tx, _is_async_db

log = logging.getLogger(__name__)

# Canonical anchors for system steps (ordering uses these symbolic anchors)
START_TX = "START_TX"
HANDLER = "HANDLER"
END_TX = "END_TX"

# Runner signature (matches atoms): (obj|None, ctx) -> None
SysRunFn = Callable[[Optional[object], Any], None]


# ──────────────────────────────────────────────────────────────────────────────
# Pluggable runners (adapters install real implementations at app startup)
# ──────────────────────────────────────────────────────────────────────────────


class _Installed:
    begin: Optional[Callable[[Any], None]] = None  # (ctx) -> None
    handler: Optional[Callable[[Optional[object], Any], None]] = (
        None  # (obj, ctx) -> None
    )
    commit: Optional[Callable[[Any], None]] = None  # (ctx) -> None
    rollback: Optional[Callable[[Any, BaseException | None], None]] = (
        None  # (ctx, err) -> None
    )


INSTALLED = _Installed()  # singleton container


def install(
    *,
    begin: Optional[Callable[[Any], None]] = None,
    handler: Optional[Callable[[Optional[object], Any], None]] = None,
    commit: Optional[Callable[[Any], None]] = None,
    rollback: Optional[Callable[[Any, BaseException | None], None]] = None,
) -> None:
    """
    Adapter entrypoint to install concrete system step functions.

    Example (SQLAlchemy-ish pseudocode):
        from tigrbl.runtime import system as sys
        sys.install(
            begin=lambda ctx: ctx.session.begin(),
            handler=lambda obj, ctx: ctx.route_handler(obj, ctx),
            commit=lambda ctx: ctx.session.commit(),
            rollback=lambda ctx, err: ctx.session.rollback(),
        )
    """
    if begin is not None:
        INSTALLED.begin = begin
    if handler is not None:
        INSTALLED.handler = handler
    if commit is not None:
        INSTALLED.commit = commit
    if rollback is not None:
        INSTALLED.rollback = rollback


# ──────────────────────────────────────────────────────────────────────────────
# Default implementations (safe no-ops except handler, which errs if missing)
# ──────────────────────────────────────────────────────────────────────────────


def _sys_tx_begin(_obj: Optional[object], ctx: Any) -> None:
    """
    sys:txn:begin — open a transaction/savepoint if the adapter installed a runner.
    Defaults to no-op; sets a small flag for diagnostics.
    """
    log.debug("system: begin_tx enter")
    _ensure_temp(ctx)
    has_open = any(
        callable(fn) for fn in (INSTALLED.begin, INSTALLED.commit, INSTALLED.rollback)
    )
    ctx.temp["__sys_tx_open__"] = has_open
    try:
        if callable(INSTALLED.begin):
            INSTALLED.begin(ctx)
            log.debug("system: begin_tx executed.")
        else:
            log.debug("system: begin_tx no-op (no adapter installed).")
    except Exception as e:  # escalate as typed error
        ctx.temp["__sys_tx_open__"] = False
        raise _err.SystemStepError("Failed to begin transaction.", cause=e)
    finally:
        log.debug("system: begin_tx exit")


def _sys_handler_crud(obj: Optional[object], ctx: Any) -> None:
    """
    sys:handler:crud — invoke the model/router handler.
    Resolution order:
      1) Installed adapter runner (INSTALLED.handler)
      2) ctx.temp['handler'] if callable
      3) getattr(ctx, 'handler')
      4) getattr(ctx.model, 'runtime').handler or ctx.model.handler
    On total miss, raises SystemStepError.
    """
    try:
        # 1) Adapter-installed
        if callable(INSTALLED.handler):
            return INSTALLED.handler(obj, ctx)

        # 2) From ctx.temp (explicitly staged by adapter)
        h = _get_temp(ctx).get("handler")
        if callable(h):
            return h(obj, ctx)

        # 3) Directly on ctx (adapters may set this)
        h = getattr(ctx, "handler", None)
        if callable(h):
            return h(obj, ctx)

        # 4) On the model (common pattern: Model.runtime.handler / Model.handler)
        mdl = getattr(ctx, "model", None)
        if mdl is not None:
            r = getattr(getattr(mdl, "runtime", None), "handler", None)
            if callable(r):
                return r(obj, ctx)
            r = getattr(mdl, "handler", None)
            if callable(r):
                return r(obj, ctx)

        # No handler found
        raise _err.SystemStepError(
            "No handler is installed or discoverable for this operation."
        )

    except _err.TigrblError:
        # Pass through typed errors intact
        raise
    except Exception as e:
        raise _err.SystemStepError("Handler execution failed.", cause=e)


async def _sys_tx_commit(_obj: Optional[object], ctx: Any) -> None:
    """
    sys:txn:commit — commit the transaction if begin ran and adapter installed commit.
    Defaults to no-op; clears the 'open' flag.
    """
    log.debug("system: commit_tx enter")
    _ensure_temp(ctx)
    db = getattr(ctx, "db", None)
    open_flag = bool(ctx.temp.get("__sys_tx_open__")) or (db is not None and _in_tx(db))
    try:
        if open_flag:
            if callable(INSTALLED.commit):
                rv = INSTALLED.commit(ctx)
                if inspect.isawaitable(rv):
                    await rv  # type: ignore[func-returns-value]
                log.debug("system: commit_tx executed.")
            else:
                log.debug("system: commit_tx no-op (no adapter commit).")

            if db is not None and _in_tx(db):
                log.debug("system: commit_tx fallback commit executing.")
                commit = getattr(db, "commit", None)
                if callable(commit):
                    try:
                        if _is_async_db(db):
                            await commit()  # type: ignore[misc]
                        else:
                            commit()
                        log.debug("system: commit_tx fallback commit succeeded.")
                    except Exception as e:  # pragma: no cover - defensive safeguard
                        log.exception("system: commit_tx fallback commit failed: %s", e)
                else:
                    log.debug(
                        "system: commit_tx fallback commit not possible (no commit attr)."
                    )
        else:
            log.debug("system: commit_tx no-op (open=%s).", open_flag)
    except Exception as e:
        raise _err.SystemStepError("Failed to commit transaction.", cause=e)
    finally:
        ctx.temp["__sys_tx_open__"] = False
        log.debug("system: commit_tx exit")


def run_rollback(ctx: Any, err: BaseException | None = None) -> None:
    """
    Execute rollback logic when the kernel catches an exception.
    Always safe to call (even if no begin was executed).
    """
    try:
        if callable(INSTALLED.rollback):
            INSTALLED.rollback(ctx, err)
            log.debug("system: rollback executed.")
        else:
            # Best-effort fallback: try common session attribute
            sess = getattr(ctx, "session", None)
            rb = getattr(sess, "rollback", None)
            if callable(rb):
                rb()
                log.debug("system: rollback via ctx.session.rollback().")
    except Exception as e:  # Never mask the original error; log only.
        log.exception("system: rollback failed: %s", e)


# ──────────────────────────────────────────────────────────────────────────────
# Registry & dispatch (mirrors atoms registry shape for consistency)
# ──────────────────────────────────────────────────────────────────────────────

REGISTRY: Dict[Tuple[str, str], Tuple[str, SysRunFn]] = {
    ("txn", "begin"): (START_TX, _sys_tx_begin),
    ("handler", "crud"): (HANDLER, _sys_handler_crud),
    ("txn", "commit"): (END_TX, _sys_tx_commit),
}


def get(domain: str, subject: str) -> Tuple[str, SysRunFn]:
    """
    Return (anchor, runner) for a given system step, e.g., get('txn','begin').
    """
    key = (domain, subject)
    if key not in REGISTRY:
        raise KeyError(f"Unknown system step: {domain}:{subject}")
    return REGISTRY[key]


def subjects(domain: str | None = None) -> Tuple[Tuple[str, str], ...]:
    """
    Return the available (domain, subject) tuples, optionally filtered by domain.
    """
    items = tuple(sorted(REGISTRY.keys()))
    if domain is None:
        return items
    return tuple(k for k in items if k[0] == domain)


def all_items() -> Tuple[Tuple[Tuple[str, str], Tuple[str, SysRunFn]], ...]:
    """Return the registry items as a sorted tuple (deterministic iteration)."""
    return tuple(sorted(REGISTRY.items(), key=lambda kv: (kv[0][0], kv[0][1])))


# ──────────────────────────────────────────────────────────────────────────────
# Internals
# ──────────────────────────────────────────────────────────────────────────────


def _ensure_temp(ctx: Any) -> MutableMapping[str, Any]:
    tmp = getattr(ctx, "temp", None)
    if not isinstance(tmp, dict):
        tmp = {}
        setattr(ctx, "temp", tmp)
    return tmp


def _get_temp(ctx: Any) -> Mapping[str, Any]:
    tmp = getattr(ctx, "temp", None)
    return tmp if isinstance(tmp, Mapping) else {}


__all__ = [
    # anchors
    "START_TX",
    "HANDLER",
    "END_TX",
    # install surface
    "install",
    "INSTALLED",
    # rollback
    "run_rollback",
    # registry facade
    "REGISTRY",
    "get",
    "subjects",
    "all_items",
]
