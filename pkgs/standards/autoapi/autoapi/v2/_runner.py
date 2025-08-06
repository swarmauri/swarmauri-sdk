from __future__ import annotations

from inspect import isawaitable, iscoroutinefunction
from typing import Callable, Mapping, MutableMapping, Any, Optional
from types import SimpleNamespace

from .hooks import Phase


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
    Unified execution engine used by *both* JSON-RPC gateway **and** REST routes.

    Args
    ----
    api       : AutoAPI instance (provides ._run, .rpc, .authorize …)
    method    : canonical RPC id, e.g. ``"User.create"``
    params    : flat dict of parameters (exactly what JSON-RPC would carry)
    ctx       : mutable context injected into every hook
                ─ keys **required** so far: ``request``, ``db``, ``env``
    exec_fn   : optional delegate that knows how to execute the business
                function inside an AsyncSession’s `run_sync`.  REST routes that
                hold an `AsyncSession` supply this, otherwise leave *None*.

    Returns
    -------
    The raw result (dict / list / pydantic dump) produced by the business func.
    """
    db = ctx["db"]

    try:
        # ─── PRE hook ────────────────────────────────────────────────────────
        await api._run(Phase.PRE_TX_BEGIN, ctx)

        # Allow hooks to mutate request parameters via ``ctx['env'].params``
        params = ctx["env"].params

        # ─── business logic call -------------------------------------------
        if exec_fn is not None:  # custom executor
            maybe = exec_fn(method, params, db)
            result = await maybe if isawaitable(maybe) else maybe
        else:
            maybe = api.rpc[method](params, db)
            result = await maybe if isawaitable(maybe) else maybe

        ctx["result"] = result
        await api._run(Phase.POST_HANDLER, ctx)

        # ─── commit (sync *or* async) --------------------------------------
        if db.in_transaction():
            await api._run(Phase.PRE_COMMIT, ctx)

            if iscoroutinefunction(db.commit):
                await db.commit()  # AsyncSession
            else:
                db.commit()  # plain Session

            await api._run(Phase.POST_COMMIT, ctx)

        result = ctx.get("result", result)

        # ─── POST hook ------------------------------------------------------
        ctx["response"] = SimpleNamespace(result=result)
        await api._run(Phase.POST_RESPONSE, ctx)
        return ctx["response"].result

    # ─────────────── error path ─────────────────────────────────────────────
    except Exception as exc:
        if db.in_transaction():
            if iscoroutinefunction(db.rollback):
                await db.rollback()
            else:
                db.rollback()

        ctx["exc"] = exc
        await api._run(Phase.ON_ERROR, ctx)
        raise
