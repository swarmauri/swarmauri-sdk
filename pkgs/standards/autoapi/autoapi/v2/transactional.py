"""
autoapi.v2.transactional
========================
A single decorator that

• wraps a handler in an explicit SQLAlchemy transaction (sync *and* async)
• registers it in ``api.rpc["<name>"]``
• exposes a thin REST façade (default ``POST /<name>``) that forwards
  to the same RPC through the unified `_invoke` lifecycle engine.

Nothing else in AutoAPI needs to change.
"""

from __future__ import annotations

from functools import wraps
from inspect import isawaitable
from typing import Any, Callable, Mapping, MutableMapping

from fastapi import Body, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from ._runner import _invoke  # central lifecycle engine


def transactional(  # ← bound per-instance in AutoAPI.__init__
    self,
    fn: Callable[..., Any] | None = None,
    *,
    name: str | None = None,
    rest_path: str | None = None,
    rest_method: str = "POST",
    tags: tuple[str, ...] = ("txn",),
) -> Callable[..., Any]:
    """
    Example
    -------
        @api.transactional
        def bundle_create(params, db):
            ...
            return {"ok": True}

    Customise names / verbs:

        @api.transactional(name="bundle.create",
                           rest_path="/tx/bundle",
                           rest_method="PUT")
        async def bundle(params, db): ...
    """

    # ─── allow bare decorator or decorator with kwargs ────────────────
    if fn is None:
        return lambda real_fn: transactional(
            self,
            real_fn,
            name=name,
            rest_path=rest_path,
            rest_method=rest_method,
            tags=tags,
        )

    rpc_id = name or fn.__name__
    rest_uri = rest_path or f"/{rpc_id.replace('.', '/')}"

    # ❶  atomic-DB wrapper (sync + async) ──────────────────────────────
    def _sync(params: Mapping[str, Any], db: Session, *a, **k):
        with db.begin():
            return fn(params, db, *a, **k)

    async def _async(params: Mapping[str, Any], db: AsyncSession, *a, **k):
        async with db.begin():
            result = fn(params, db, *a, **k)
            return await result if isawaitable(result) else result

    @wraps(fn)
    def _wrapped(params: Mapping[str, Any], db: Session | AsyncSession, *a, **k):
        return (
            _async(params, db, *a, **k)
            if isinstance(db, AsyncSession)
            else _sync(params, db, *a, **k)
        )

    # ❷  RPC registration ─────────────────────────────────────────────
    if rpc_id in self.rpc:
        raise RuntimeError(f"RPC '{rpc_id}' already registered")

    self.rpc[rpc_id] = _wrapped
    if hasattr(self, "_method_ids"):  # populated by /methodz route
        self._method_ids[rpc_id] = _wrapped

    # ❸  REST façade that re-invokes via `_invoke`  ───────────────────
    if hasattr(self, "get_async_db") and self.get_async_db is not None:

        async def _rest_endpoint(
            request: Request,  #  ← ✅
            params: Mapping[str, Any] = Body(...),
            db: Session = Depends(self.get_db),
        ):
            ctx: MutableMapping[str, Any] = {"request": request, "db": db, "env": {}}
            return await _invoke(self, rpc_id, params=params, ctx=ctx)

    else:  # fallback to sync-DB dependency

        async def _rest_endpoint(
            request: Request,  #  ← ✅
            params: Mapping[str, Any] = Body(...),
            db: Session = Depends(self.get_db),
        ):
            ctx: MutableMapping[str, Any] = {"request": request, "db": db, "env": {}}
            return await _invoke(self, rpc_id, params=params, ctx=ctx)

    self.router.add_api_route(
        rest_uri,
        _rest_endpoint,
        methods=[rest_method],
        tags=list(tags),
        name=rpc_id,
    )

    return _wrapped
