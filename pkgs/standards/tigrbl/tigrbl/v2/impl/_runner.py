# tigrbl/v2/_runner.py
from __future__ import annotations

from inspect import isawaitable, iscoroutinefunction
from typing import Callable, Mapping, MutableMapping, Any, Optional
from types import SimpleNamespace

from ..hooks import Phase


class _Ctx(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


# ───────────────────────── helpers ─────────────────────────


def _is_async_session(db) -> bool:
    # AsyncSession exposes run_sync; plain Session does not
    return hasattr(db, "run_sync")


def _in_tx(db) -> bool:
    try:
        return bool(db.in_transaction())
    except Exception:
        return False


async def _rollback_safely(api, db, ctx):
    try:
        if _in_tx(db):
            if iscoroutinefunction(db.rollback):
                await db.rollback()
            else:
                db.rollback()
    finally:
        # fire ON_ROLLBACK if defined
        ph = getattr(Phase, "ON_ROLLBACK", None)
        if ph is not None:
            try:
                await api._run(ph, ctx)
            except Exception:
                # rollback hooks must not mask original errors
                pass


async def _run_phase(api, phase, ctx):
    """Run a phase if it exists; return True if it ran."""
    if phase is None:
        return False
    await api._run(phase, ctx)
    return True


def _phase(name: str):
    """Fetch a Phase member by name; returns None if not declared yet."""
    return getattr(Phase, name, None)


# ---------------------------------------------------------------------------#
async def _invoke(
    api,
    method: str,
    *,
    params: Mapping[str, Any],
    ctx: MutableMapping[str, Any],
    exec_fn: Optional[Callable[[str, Mapping[str, Any], Any], Any]] = None,
):
    """
    Unified execution engine (JSON-RPC & REST).

    Lifecycle:
      PRE_TX_BEGIN
      (begin transaction if needed)
      PRE_HANDLER
      handler
      POST_HANDLER
      PRE_COMMIT
      COMMIT
      POST_COMMIT
      POST_RESPONSE

    Error handling:
      • PRE_TX_BEGIN failure → ON_ERROR (no rollback)
      • Failures during PRE_HANDLER / handler / POST_HANDLER / PRE_COMMIT / COMMIT
          → rollback → ON_ROLLBACK → specific ON_*_ERROR (if present) else ON_ERROR
      • POST_COMMIT failure → ON_POST_COMMIT_ERROR (or ON_ERROR), then raise
      • POST_RESPONSE failure → ON_POST_RESPONSE_ERROR (or ON_ERROR), return pre-built result
    """
    ctx = _Ctx(ctx)
    db = ctx["db"]

    # ─── PRE_TX_BEGIN (no transaction) ────────────────────────────────────
    try:
        await api._run(Phase.PRE_TX_BEGIN, ctx)
    except Exception as exc:
        ctx["exc"] = exc
        # generic error phase for pre-begin failures
        await _run_phase(api, _phase("ON_ERROR"), ctx)
        raise

    # Allow hooks to rewrite method/params after PRE_TX_BEGIN
    method = getattr(ctx["env"], "method", method) or method
    params = getattr(ctx["env"], "params", params)
    ctx["payload"] = params  # legacy alias used by some hooks

    # ─── Ensure a transaction is active for handler phases ───────────────
    try:
        if not _in_tx(db):
            if _is_async_session(db):
                await db.begin()
            else:
                db.begin()
    except Exception as exc:  # unlikely, but treat as pre-handler error
        ctx["exc"] = exc
        # cannot rollback a tx we failed to begin; just signal error
        await _run_phase(api, _phase("ON_ERROR"), ctx)
        raise

    # ─── PRE_HANDLER (inside transaction; may flush) ─────────────────────
    try:
        await _run_phase(api, _phase("PRE_HANDLER"), ctx)
    except Exception as exc:
        ctx["exc"] = exc
        await _rollback_safely(api, db, ctx)
        await _run_phase(api, _phase("ON_PRE_HANDLER_ERROR") or _phase("ON_ERROR"), ctx)
        raise

    # ─── Business logic / core call (may flush) ──────────────────────────
    try:
        if exec_fn is not None:
            maybe = exec_fn(method, params, db)
            result = await maybe if isawaitable(maybe) else maybe
        else:
            # Default adapter:
            # - If we are in async mode and the RPC handler is sync, execute it
            #   inside the engine’s sync context via AsyncSession.run_sync(...),
            #   passing a real sync Session.
            # - Otherwise, call directly and await if needed.
            handler = api.rpc[method]
            if _is_async_session(db) and not iscoroutinefunction(handler):
                result = await db.run_sync(lambda s: handler(params, s))
            else:
                maybe = handler(params, db)
                result = await maybe if isawaitable(maybe) else maybe

        ctx["result"] = result
    except Exception as exc:
        ctx["exc"] = exc
        await _rollback_safely(api, db, ctx)
        await _run_phase(api, _phase("ON_HANDLER_ERROR") or _phase("ON_ERROR"), ctx)
        raise

    # ─── POST_HANDLER (still in transaction; may flush) ──────────────────
    try:
        await _run_phase(api, _phase("POST_HANDLER"), ctx)
    except Exception as exc:
        ctx["exc"] = exc
        await _rollback_safely(api, db, ctx)
        await _run_phase(
            api, _phase("ON_POST_HANDLER_ERROR") or _phase("ON_ERROR"), ctx
        )
        raise

    # ─── PRE_COMMIT ──────────────────────────────────────────────────────
    try:
        await _run_phase(api, Phase.PRE_COMMIT, ctx)
    except Exception as exc:
        ctx["exc"] = exc
        await _rollback_safely(api, db, ctx)
        await _run_phase(api, _phase("ON_PRE_COMMIT_ERROR") or _phase("ON_ERROR"), ctx)
        raise

    # ─── COMMIT ──────────────────────────────────────────────────────────
    try:
        if iscoroutinefunction(db.commit):
            await db.commit()
        else:
            db.commit()
    except Exception as exc:
        ctx["exc"] = exc
        # best-effort rollback (may already be closed by failed commit)
        await _rollback_safely(api, db, ctx)
        await _run_phase(api, _phase("ON_COMMIT_ERROR") or _phase("ON_ERROR"), ctx)
        raise

    # ─── POST_COMMIT ─────────────────────────────────────────────────────
    result = ctx.get("result")
    try:
        await _run_phase(api, Phase.POST_COMMIT, ctx)
    except Exception as exc:
        ctx["exc"] = exc
        # cannot rollback after successful commit; just report
        await _run_phase(api, _phase("ON_POST_COMMIT_ERROR") or _phase("ON_ERROR"), ctx)
        raise

    # ─── POST_RESPONSE (response shaping; non-fatal by design) ───────────
    ctx["response"] = SimpleNamespace(result=result)
    try:
        await _run_phase(api, Phase.POST_RESPONSE, ctx)
        return ctx["response"].result
    except Exception as exc:
        # Do not break the request; report via hook and return prior result
        ctx["exc"] = exc
        await _run_phase(
            api, _phase("ON_POST_RESPONSE_ERROR") or _phase("ON_ERROR"), ctx
        )
        return ctx["response"].result
