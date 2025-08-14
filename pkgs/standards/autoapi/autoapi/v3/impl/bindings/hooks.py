# autoapi/v3/bindings/hooks.py
from __future__ import annotations

import inspect
import logging
from types import SimpleNamespace
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from ..opspec import OpHook, OpSpec
from ..opspec.types import PHASES, HookPhase, StepFn

logger = logging.getLogger(__name__)

_Key = Tuple[str, str]  # (alias, target)


# ───────────────────────────────────────────────────────────────────────────────
# Helpers for ctx access
# ───────────────────────────────────────────────────────────────────────────────

def _ctx_get(ctx: Mapping[str, Any], key: str, default: Any = None) -> Any:
    try:
        return ctx[key]
    except Exception:
        return getattr(ctx, key, default)

def _ctx_db(ctx: Mapping[str, Any]) -> Any:
    return _ctx_get(ctx, "db")

def _ctx_payload(ctx: Mapping[str, Any]) -> Mapping[str, Any]:
    return _ctx_get(ctx, "payload", {}) or {}

def _is_async_db(db: Any) -> bool:
    # AsyncSession usually has run_sync/commit/flush async methods
    return hasattr(db, "run_sync") or inspect.iscoroutinefunction(getattr(db, "commit", None))


# ───────────────────────────────────────────────────────────────────────────────
# Default transactional hooks
# ───────────────────────────────────────────────────────────────────────────────

def _default_start_tx() -> StepFn:
    async def _step(ctx: Any) -> None:
        db = _ctx_db(ctx)
        if db is None:
            return
        begin = getattr(db, "begin", None)
        if begin is None:
            return
        if _is_async_db(db):
            await begin()  # type: ignore[misc]
        else:
            begin()
    return _step

def _default_end_tx() -> StepFn:
    async def _step(ctx: Any) -> None:
        db = _ctx_db(ctx)
        if db is None:
            return
        commit = getattr(db, "commit", None)
        if commit is None:
            return
        if _is_async_db(db):
            await commit()  # type: ignore[misc]
        else:
            commit()
    return _step

def _mark_skip_persist() -> StepFn:
    async def _step(ctx: Any) -> None:
        # Signal the executor to skip START/END and forbid writes
        try:
            ctx["__autoapi_skip_persist__"] = True
        except Exception:
            setattr(ctx, "__autoapi_skip_persist__", True)
    return _step


# ───────────────────────────────────────────────────────────────────────────────
# User hook wrapping (sequential; no priority)
# ───────────────────────────────────────────────────────────────────────────────

def _should_run(h: OpHook, ctx: Mapping[str, Any]) -> bool:
    pred = h.when
    if pred is None:
        return True
    payload = _ctx_payload(ctx)
    try:
        return bool(pred(payload))
    except TypeError:
        # Fallback to passing the whole ctx
        try:
            return bool(pred(ctx))  # type: ignore[misc]
        except Exception:
            logger.debug("hook predicate failed; defaulting to run: %r", h, exc_info=True)
            return True
    except Exception:
        logger.debug("hook predicate error; defaulting to run: %r", h, exc_info=True)
        return True

def _wrap_hook(h: OpHook) -> StepFn:
    fn = h.fn
    async def _step(ctx: Any) -> Any:
        if not _should_run(h, ctx):
            return None
        rv = fn(ctx)
        if inspect.isawaitable(rv):
            return await rv
        return rv
    return _step


# ───────────────────────────────────────────────────────────────────────────────
# Namespace helpers
# ───────────────────────────────────────────────────────────────────────────────

def _ensure_alias_hooks_ns(model: type, alias: str) -> SimpleNamespace:
    root = getattr(model, "hooks", None)
    if root is None:
        root = SimpleNamespace()
        setattr(model, "hooks", root)
    ns = getattr(root, alias, None)
    if ns is None:
        ns = SimpleNamespace()
        setattr(root, alias, ns)
    # Ensure all known phases exist as lists (executor expects lists of steps)
    for ph in PHASES:
        if not hasattr(ns, ph):
            setattr(ns, ph, [])
    return ns


# ───────────────────────────────────────────────────────────────────────────────
# Build / attach
# ───────────────────────────────────────────────────────────────────────────────

def _attach_one(model: type, sp: OpSpec) -> None:
    """
    Build ordered phase chains for this OpSpec and attach under model.hooks.<alias>.
    Execution is strictly sequential in each phase; no sorting or numeric priorities.
    """
    alias = sp.alias
    ns = _ensure_alias_hooks_ns(model, alias)

    # Reset all phase chains for this alias (we rebuild afresh)
    for ph in PHASES:
        setattr(ns, ph, [])

    # Ephemeral ops: mark skip & skip start/end tx
    if sp.persist == "skip":
        getattr(ns, "PRE_TX_BEGIN").append(_mark_skip_persist())
    else:
        # Persistent: START_TX first, END_TX last
        getattr(ns, "START_TX").append(_default_start_tx())

    # Add user hooks in the exact order they were declared
    for h in sp.hooks or ():
        phase: HookPhase = h.phase  # type: ignore[assignment]
        if phase not in PHASES:
            logger.warning("Unknown hook phase %r on %s.%s; skipping", phase, model.__name__, alias)
            continue
        getattr(ns, phase).append(_wrap_hook(h))

    # Persistent END_TX last
    if sp.persist != "skip":
        getattr(ns, "END_TX").append(_default_end_tx())

    logger.debug("hooks: %s.%s -> phases prepared (persist=%s)", model.__name__, alias, sp.persist)


def normalize_and_attach(model: type, specs: Sequence[OpSpec], *, only_keys: Optional[Sequence[_Key]] = None) -> None:
    """
    Build sequential phase chains for each OpSpec and attach them to model.hooks.<alias>.
    If `only_keys` is provided, limit work to those (alias,target) pairs.
    """
    wanted = set(only_keys or ())
    for sp in specs:
        key = (sp.alias, sp.target)
        if wanted and key not in wanted:
            continue
        _attach_one(model, sp)


__all__ = ["normalize_and_attach"]
