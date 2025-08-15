# autoapi/v3/transport/jsonrpc/dispatcher.py
"""
JSON-RPC 2.0 dispatcher for AutoAPI v3.

This module exposes a single helper:

    build_jsonrpc_router(api, *, get_db=None, get_async_db=None) -> APIRouter

- It mounts a POST endpoint at "/" that accepts either a single JSON-RPC request
  object or a batch (array) of request objects.
- Each JSON-RPC `method` must be of the form "Model.alias". The dispatcher will
  look up `api.models["Model"]`, then call the bound coroutine at
  `Model.rpc.<alias>(params, *, db, request, ctx)`.
- Input validation and output shaping are handled by the per-op RPC wrappers
  built in `autoapi.v3.bindings.rpc`.
- Errors are converted to JSON-RPC error objects using the v3 runtime error
  mappers (HTTP → RPC codes).

You would usually mount the returned router at `/rpc`, e.g.:

    app.include_router(build_jsonrpc_router(api), prefix="/rpc")
"""

from __future__ import annotations

import logging
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Mapping,
    Optional,
    Sequence,
)

try:
    from fastapi import APIRouter, Request, Body, Depends, HTTPException
    from fastapi.responses import Response
except Exception:  # pragma: no cover
    # Minimal shims to keep this importable without FastAPI (for typing/tools)
    class APIRouter:  # type: ignore
        def __init__(self, *a, **kw):
            self.routes = []

        def add_api_route(
            self, path: str, endpoint: Callable, methods: Sequence[str], **opts
        ):
            self.routes.append((path, methods, endpoint, opts))

    class Request:  # type: ignore
        def __init__(self, scope=None):
            self.scope = scope or {}
            self.state = type("S", (), {})()
            self.query_params = {}

        async def json(self) -> Any:
            return {}

    def Body(default=None, **kw):  # type: ignore
        return default

    def Depends(fn):  # type: ignore
        return fn

    class Response:  # type: ignore
        def __init__(self, status_code: int = 200, content: Any = None):
            self.status_code = status_code
            self.body = content

    class HTTPException(Exception):  # type: ignore
        def __init__(self, status_code: int, detail: Any = None):
            super().__init__(detail)
            self.status_code = status_code
            self.detail = detail


from ...runtime.errors import (
    ERROR_MESSAGES,
)
from ...v2.jsonrpc_models import _http_exc_to_rpc

logger = logging.getLogger(__name__)

Json = Mapping[str, Any]
Batch = Sequence[Mapping[str, Any]]

# --------------------------------------------------------------------------- #
# Utilities
# --------------------------------------------------------------------------- #


def _ok(result: Any, id_: Any) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "result": result, "id": id_}


def _err(code: int, msg: str, id_: Any, data: Any | None = None) -> Dict[str, Any]:
    e: Dict[str, Any] = {
        "jsonrpc": "2.0",
        "error": {"code": code, "message": msg},
        "id": id_,
    }
    if data is not None:
        e["error"]["data"] = data
    return e


def _normalize_params(params: Any) -> Mapping[str, Any]:
    if params is None:
        return {}
    if isinstance(params, Mapping):
        return dict(params)
    # Positional params are not supported in AutoAPI adapters
    raise HTTPException(status_code=400, detail="Invalid params: expected object")


def _model_for(api: Any, name: str) -> Optional[type]:
    models: Dict[str, type] = getattr(api, "models", {}) or {}
    mdl = models.get(name)
    if mdl is not None:
        return mdl
    # Case-insensitive fallback
    lower = name.lower()
    for k, v in models.items():
        if k.lower() == lower:
            return v
    return None


async def _dispatch_one(
    *,
    api: Any,
    request: Request,
    db: Any,
    obj: Mapping[str, Any],
) -> Optional[Dict[str, Any]]:
    """
    Handle a single JSON-RPC request object and return a response dict,
    or None if it's a "notification" (no id field).
    """
    rid = obj.get("id", None)
    try:
        # Basic JSON-RPC validation
        if not isinstance(obj, Mapping):
            return _err(-32600, "Invalid Request", rid)  # not an object
        if obj.get("jsonrpc") != "2.0":
            return _err(-32600, "Invalid Request", rid)
        method = obj.get("method")
        if not isinstance(method, str) or "." not in method:
            return _err(-32601, "Method not found", rid)

        model_name, alias = method.split(".", 1)
        model = _model_for(api, model_name)
        if model is None:
            return _err(-32601, f"Unknown model '{model_name}'", rid)

        # Locate RPC callable built by bindings.rpc
        rpc_ns = getattr(model, "rpc", None)
        rpc_call = getattr(rpc_ns, alias, None)
        if rpc_call is None:
            return _err(-32601, f"Method not found: {model_name}.{alias}", rid)

        # Params
        try:
            params = _normalize_params(obj.get("params"))
        except HTTPException as exc:
            code, msg, data = _http_exc_to_rpc(exc)
            return _err(code, msg, rid, data)

        # Compose a context; allow middlewares to seed request.state.ctx
        base_ctx: Dict[str, Any] = {}
        extra_ctx = getattr(request.state, "ctx", None)
        if isinstance(extra_ctx, Mapping):
            base_ctx.update(extra_ctx)
        base_ctx.setdefault("rpc_id", rid)

        # Execute
        result = await rpc_call(params, db=db, request=request, ctx=base_ctx)

        # Notification: no response
        if rid is None:
            return None
        return _ok(result, rid)

    except HTTPException as exc:
        code, msg, data = _http_exc_to_rpc(exc)
        # Notifications still don't produce output
        if rid is None:
            return None
        return _err(code, msg, rid, data)
    except Exception:
        logger.exception("jsonrpc dispatch failed")
        # Internal error (per JSON-RPC); do not leak details
        if rid is None:
            return None
        return _err(-32603, ERROR_MESSAGES.get(-32603, "Internal error"), rid)


# --------------------------------------------------------------------------- #
# Public router factory
# --------------------------------------------------------------------------- #


def build_jsonrpc_router(
    api: Any,
    *,
    get_db: Optional[Callable[..., Any]] = None,
    get_async_db: Optional[Callable[..., Awaitable[Any]]] = None,
) -> APIRouter:
    """
    Build and return an APIRouter that serves a single POST endpoint at "/".
    Mount it at your preferred prefix (e.g., "/rpc").

    If `get_async_db` or `get_db` is provided, it will be used as a FastAPI
    dependency for obtaining a DB session/connection. If neither is provided,
    the dispatcher will try to use `request.state.db` (or pass `db=None`).
    """
    router = APIRouter()
    dep = get_async_db or get_db  # Prefer async DB getter if present

    if dep is not None:
        # Inject DB via FastAPI dependency for proper lifecycle management.
        async def _endpoint(
            request: Request, body: Any = Body(...), db: Any = Depends(dep)
        ):
            # Accept single or batch requests
            if isinstance(body, list):
                responses: List[Dict[str, Any]] = []
                for item in body:
                    resp = await _dispatch_one(
                        api=api, request=request, db=db, obj=item
                    )
                    if resp is not None:
                        responses.append(resp)
                # Per JSON-RPC: an empty response array is valid for a batch of only notifications.
                return responses
            elif isinstance(body, Mapping):
                resp = await _dispatch_one(api=api, request=request, db=db, obj=body)
                # Notification → 204 No Content
                if resp is None:
                    return Response(status_code=204)
                return resp
            else:
                # Parse error / invalid request shape
                return _err(-32600, "Invalid Request", None)
    else:
        # No dependency; attempt to read db from request.state.db
        async def _endpoint(request: Request, body: Any = Body(...)):
            db = getattr(request.state, "db", None)
            if isinstance(body, list):
                responses: List[Dict[str, Any]] = []
                for item in body:
                    resp = await _dispatch_one(
                        api=api, request=request, db=db, obj=item
                    )
                    if resp is not None:
                        responses.append(resp)
                return responses
            elif isinstance(body, Mapping):
                resp = await _dispatch_one(api=api, request=request, db=db, obj=body)
                if resp is None:
                    return Response(status_code=204)
                return resp
            else:
                return _err(-32600, "Invalid Request", None)

    # Attach route (POST "/")
    router.add_api_route(
        path="/",
        endpoint=_endpoint,
        methods=["POST"],
        name="autoapi.jsonrpc",
    )
    return router


__all__ = ["build_jsonrpc_router"]
