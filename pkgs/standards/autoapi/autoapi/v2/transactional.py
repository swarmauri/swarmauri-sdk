"""
autoapi.v2.transactional
========================
A single decorator that

• registers the handler in ``api.rpc["<name>"]``
• exposes a thin REST façade (default ``POST /<name>``) that forwards
  to the same RPC through the unified `_invoke` lifecycle engine,
  which now owns the transaction lifecycle

Nothing else in AutoAPI needs to change.
"""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable, Mapping, MutableMapping

from fastapi import Body, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from .impl._runner import _invoke  # central lifecycle engine


def register_transaction(
    self,
    rpc_id: str,
    fn: Callable[..., Any],
    rest_uri: str,
    *,
    rest_method: str = "POST",
    tags: tuple[str, ...] = ("txn",),
) -> None:
    """Register an RPC handler and expose a REST endpoint.

    Parameters
    ----------
    self:
        The :class:`AutoAPI` instance to bind to.
    rpc_id:
        JSON-RPC method name. Must be unique across the API instance.
    fn:
        Callable invoked when the RPC executes.
    rest_uri:
        Path for the REST façade that forwards to the RPC.
    rest_method:
        HTTP method for the REST route. Defaults to ``"POST"``.
    tags:
        Optional FastAPI tags applied to the generated route.

    Raises
    ------
    RuntimeError
        If ``rpc_id`` is already registered or if the REST route cannot be
        created.
    """
    if rpc_id in self.rpc:
        raise RuntimeError(f"RPC '{rpc_id}' already registered")

    self.rpc[rpc_id] = fn
    if hasattr(self, "_method_ids"):  # populated by /methodz route
        self._method_ids[rpc_id] = fn

    if hasattr(self, "get_async_db") and self.get_async_db is not None:

        async def _rest_endpoint(
            request: Request,
            params: Mapping[str, Any] = Body(...),
            db: AsyncSession = Depends(self.get_async_db),
        ):
            ctx: MutableMapping[str, Any] = {"request": request, "db": db, "env": {}}
            return await _invoke(self, rpc_id, params=params, ctx=ctx)

    else:  # fallback to sync-DB dependency

        async def _rest_endpoint(
            request: Request,
            params: Mapping[str, Any] = Body(...),
            db: Session = Depends(self.get_db),
        ):
            ctx: MutableMapping[str, Any] = {"request": request, "db": db, "env": {}}
            return await _invoke(self, rpc_id, params=params, ctx=ctx)

    try:
        self.router.add_api_route(
            rest_uri,
            _rest_endpoint,
            methods=[rest_method],
            tags=list(tags),
            name=rpc_id,
        )
    except Exception as exc:  # pragma: no cover - defensive
        self.rpc.pop(rpc_id, None)
        if hasattr(self, "_method_ids"):
            self._method_ids.pop(rpc_id, None)
        raise RuntimeError(f"Failed to register transaction '{rpc_id}'") from exc


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

    # ❶  simple wrapper – transaction handled by `_invoke` ────────────
    @wraps(fn)
    def _wrapped(params: Mapping[str, Any], db: Session | AsyncSession, *a, **k):
        return fn(params, db, *a, **k)

    self.register_transaction(
        rpc_id, _wrapped, rest_uri, rest_method=rest_method, tags=tags
    )

    return _wrapped
