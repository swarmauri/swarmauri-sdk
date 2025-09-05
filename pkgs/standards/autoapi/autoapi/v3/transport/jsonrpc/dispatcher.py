# autoapi/v3/transport/jsonrpc/dispatcher.py
"""
JSON-RPC 2.0 dispatcher for AutoAPI v3.

This module exposes a single helper:

    build_jsonrpc_router(api, *, get_db=None) -> Router

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
    Callable,
    Dict,
    List,
    Mapping,
    Optional,
    Sequence,
)

try:
    from ...types import Router, Request, Body, Depends, HTTPException, Response
except Exception:  # pragma: no cover
    # Minimal shims to keep this importable without FastAPI (for typing/tools)
    class Router:  # type: ignore
        def __init__(self, *a, **kw):
            self.routes = []
            self.dependencies = kw.get("dependencies", [])  # for parity

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


from ...runtime.errors import ERROR_MESSAGES, http_exc_to_rpc
from ...config.constants import AUTOAPI_AUTH_CONTEXT_ATTR
from .models import RPCRequest, RPCResponse

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


def _normalize_params(params: Any) -> Any:
    if params is None:
        return {}
    if isinstance(params, Mapping):
        return dict(params)
    if isinstance(params, Sequence) and not isinstance(params, (str, bytes)):
        return list(params)
    raise HTTPException(
        status_code=400, detail="Invalid params: expected object or array"
    )


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


def _user_from_request(request: Request) -> Any | None:
    return getattr(request.state, "user", None)


def _select_auth_dep(api: Any):
    """
    Choose the appropriate auth dependency based on API flags.
    Order:
      1) optional if provided,
      2) required when allow_anon == False and _authn exists,
      3) otherwise _authn if present,
      4) else None.
    """
    if getattr(api, "_optional_authn_dep", None):
        return api._optional_authn_dep
    if getattr(api, "_allow_anon", True) is False and getattr(api, "_authn", None):
        return api._authn
    if getattr(api, "_authn", None):
        return api._authn
    return None


def _normalize_deps(deps: Optional[Sequence[Any]]) -> list:
    """Accept either Depends(...) objects or plain callables."""
    out = []
    for d in deps or ():
        try:
            is_dep_obj = hasattr(d, "dependency")
        except Exception:
            is_dep_obj = False
        out.append(d if is_dep_obj else Depends(d))
    return out


def _authorize(
    api: Any,
    request: Request,
    model: type,
    alias: str,
    payload: Mapping[str, Any],
    user: Any | None,
):
    """
    Call an authorize gate if present. Prefer api._authorize; else model.__autoapi_authorize__.
    Falsy returns or exceptions (non-HTTPException) become 403.
    """
    fn = getattr(api, "_authorize", None) or getattr(
        model, "__autoapi_authorize__", None
    )
    if not fn:
        return
    try:
        rv = fn(request=request, model=model, alias=alias, payload=payload, user=user)
        if rv is False:
            raise HTTPException(status_code=403, detail="Forbidden")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=403, detail="Forbidden")


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
    rid = obj.get("id", 1)
    try:
        # Basic JSON-RPC validation
        if not isinstance(obj, Mapping):
            return _err(-32600, "Invalid Request", rid)  # not an object
        # Be lenient: default to 2.0 when "jsonrpc" is omitted
        if obj.get("jsonrpc", "2.0") != "2.0":
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
            code, msg, data = http_exc_to_rpc(exc)
            return _err(code, msg, rid, data)

        # Enforce auth when required
        if getattr(api, "_authn", None):
            method_id = f"{model.__name__}.{alias}"
            allow = getattr(api, "_allow_anon_ops", set())
            user = _user_from_request(request)
            if method_id not in allow and user is None:
                raise HTTPException(status_code=401, detail="Unauthorized")

        # Compose a context; allow middlewares to seed request.state.ctx
        base_ctx: Dict[str, Any] = {}
        extra_ctx = getattr(request.state, "ctx", None)
        if isinstance(extra_ctx, Mapping):
            base_ctx.update(extra_ctx)
        base_ctx.setdefault("rpc_id", rid)
        ac = getattr(request.state, AUTOAPI_AUTH_CONTEXT_ATTR, None)
        if ac is not None:
            base_ctx["auth_context"] = ac

        # Authorize (auth dep may already have raised; user may be on request.state)
        _authorize(api, request, model, alias, params, _user_from_request(request))

        # Execute
        result = await rpc_call(params, db=db, request=request, ctx=base_ctx)

        return _ok(result, rid)

    except HTTPException as exc:
        code, msg, data = http_exc_to_rpc(exc)
        return _err(code, msg, rid, data)
    except Exception:
        logger.exception("jsonrpc dispatch failed")
        # Internal error (per JSON-RPC); do not leak details
        return _err(-32603, ERROR_MESSAGES.get(-32603, "Internal error"), rid)


# --------------------------------------------------------------------------- #
# Public router factory
# --------------------------------------------------------------------------- #


def build_jsonrpc_router(
    api: Any,
    *,
    get_db: Optional[Callable[..., Any]] = None,
    tags: Sequence[str] | None = ("rpc",),
) -> Router:
    """
    Build and return a Router that serves a single POST endpoint at "/".
    Mount it at your preferred prefix (e.g., "/rpc").

    If `get_db` is provided, it will be used as a FastAPI
    dependency for obtaining a DB session/connection. If not provided,
    the dispatcher will try to use `request.state.db` (or pass `db=None`).

    Security:
        • If `api._authn` (or `api._optional_authn_dep`) is set, we inject it as a dependency
          so it runs before dispatch. It may set `request.state.user` and/or raise 401.
        • If `api._authorize` is set, we call it before executing the op; False/exception → 403.
        • Additional router-level dependencies can be provided via `api.rpc_dependencies`.

    The generated endpoint is tagged as "rpc" by default. Supply a custom
    sequence via ``tags`` to override or set ``None`` to omit tags.
    """
    # Extra router-level deps (e.g., tracing, IP allowlist)
    extra_router_deps = _normalize_deps(getattr(api, "rpc_dependencies", None))
    router = Router(dependencies=extra_router_deps or None)

    dep = get_db
    auth_dep = _select_auth_dep(api)

    if dep is not None and auth_dep is not None:
        # Inject both DB and user via Depends
        async def _endpoint(
            request: Request,
            body: RPCRequest | list[RPCRequest] = Body(...),
            db: Any = Depends(dep),
            user: Any = Depends(auth_dep),
        ):
            # set state for downstream handlers if dep returned user
            try:
                if user is not None and not hasattr(request.state, "user"):
                    setattr(request.state, "user", user)
            except Exception:
                pass

            if isinstance(body, list):
                responses: List[Dict[str, Any]] = []
                for item in body:
                    resp = await _dispatch_one(
                        api=api, request=request, db=db, obj=item.model_dump()
                    )
                    if resp is not None:
                        responses.append(resp)
                return responses
            elif isinstance(body, RPCRequest):
                resp = await _dispatch_one(
                    api=api, request=request, db=db, obj=body.model_dump()
                )
                if resp is None:
                    return Response(status_code=204)
                return resp
            else:
                return _err(-32600, "Invalid Request", None)

    elif dep is not None:
        # Only DB dependency
        async def _endpoint(
            request: Request,
            body: RPCRequest | list[RPCRequest] = Body(...),
            db: Any = Depends(dep),
        ):
            if isinstance(body, list):
                responses: List[Dict[str, Any]] = []
                for item in body:
                    resp = await _dispatch_one(
                        api=api, request=request, db=db, obj=item.model_dump()
                    )
                    if resp is not None:
                        responses.append(resp)
                return responses
            elif isinstance(body, RPCRequest):
                resp = await _dispatch_one(
                    api=api, request=request, db=db, obj=body.model_dump()
                )
                if resp is None:
                    return Response(status_code=204)
                return resp
            else:
                return _err(-32600, "Invalid Request", None)

    elif auth_dep is not None:
        # Only auth dependency; DB will come from request.state.db
        async def _endpoint(
            request: Request,
            body: RPCRequest | list[RPCRequest] = Body(...),
            user: Any = Depends(auth_dep),
        ):
            try:
                if user is not None and not hasattr(request.state, "user"):
                    setattr(request.state, "user", user)
            except Exception:
                pass

            db = getattr(request.state, "db", None)
            if isinstance(body, list):
                responses: List[Dict[str, Any]] = []
                for item in body:
                    resp = await _dispatch_one(
                        api=api, request=request, db=db, obj=item.model_dump()
                    )
                    if resp is not None:
                        responses.append(resp)
                return responses
            elif isinstance(body, RPCRequest):
                resp = await _dispatch_one(
                    api=api, request=request, db=db, obj=body.model_dump()
                )
                if resp is None:
                    return Response(status_code=204)
                return resp
            else:
                return _err(-32600, "Invalid Request", None)

    else:
        # No dependencies; attempt to read db (and user) from request.state
        async def _endpoint(
            request: Request, body: RPCRequest | list[RPCRequest] = Body(...)
        ):
            db = getattr(request.state, "db", None)
            if isinstance(body, list):
                responses: List[Dict[str, Any]] = []
                for item in body:
                    resp = await _dispatch_one(
                        api=api, request=request, db=db, obj=item.model_dump()
                    )
                    if resp is not None:
                        responses.append(resp)
                return responses
            elif isinstance(body, RPCRequest):
                resp = await _dispatch_one(
                    api=api, request=request, db=db, obj=body.model_dump()
                )
                if resp is None:
                    return Response(status_code=204)
                return resp
            else:
                return _err(-32600, "Invalid Request", None)

    # Attach routes for both "/rpc" and "/rpc/"
    router.add_api_route(
        path="",
        endpoint=_endpoint,
        methods=["POST"],
        name="jsonrpc",
        tags=list(tags) if tags else None,
        summary="JSONRPC",
        description="JSON-RPC 2.0 endpoint.",
        response_model=RPCResponse | list[RPCResponse],
        # extra router deps already applied via Router(dependencies=...)
    )

    # Compatibility: serve same endpoint without trailing slash
    router.add_api_route(
        path="/",
        endpoint=_endpoint,
        methods=["POST"],
        name="jsonrpc_alt",
        include_in_schema=False,
        response_model=RPCResponse | list[RPCResponse],
    )
    return router


__all__ = ["build_jsonrpc_router"]
