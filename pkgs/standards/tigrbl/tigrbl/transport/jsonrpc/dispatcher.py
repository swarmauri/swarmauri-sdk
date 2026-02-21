# tigrbl/v3/transport/jsonrpc/dispatcher.py
"""
JSON-RPC 2.0 dispatcher for Tigrbl v3.

This module exposes a single helper:

    build_jsonrpc_router(api, *, get_db=None) -> Router

- It mounts a POST endpoint at "/" that accepts either a single JSON-RPC request
  object or a batch (array) of request objects.
- Each JSON-RPC `method` must be of the form "Model.alias". The dispatcher will
  look up `api.models["Model"]`, then call the bound coroutine at
  `Model.rpc.<alias>(params, *, db, request, ctx)`.
- Input validation and output shaping are handled by the per-op RPC wrappers
  built in `tigrbl.bindings.rpc`.
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
    from ...responses import JSONResponse
except Exception:  # pragma: no cover
    # Minimal shims to keep this importable without ASGI (for typing/tools)
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

    class JSONResponse(Response):  # type: ignore
        def __init__(self, content: Any = None, status_code: int = 200):
            super().__init__(status_code=status_code, content=content)

    class HTTPException(Exception):  # type: ignore
        def __init__(self, status_code: int, detail: Any = None):
            super().__init__(detail)
            self.status_code = status_code
            self.detail = detail


from ...runtime.status import ERROR_MESSAGES, _RPC_TO_HTTP, http_exc_to_rpc
from ...transport.dispatch import dispatch_operation, resolve_model, resolve_target
from ...bindings.rpc import (
    _allowed_wrapper_keys,
    _coerce_payload,
    _reject_wrapper_keys,
    _serialize_output as _rpc_serialize_output,
    _validate_input,
)
from .models import RPCRequest, RPCResponse
from .helpers import (
    _authorize,
    _err,
    _normalize_deps,
    _normalize_params,
    _ok,
    _select_auth_dep,
    _user_from_request,
)

logger = logging.getLogger(__name__)

Json = Mapping[str, Any]
Batch = Sequence[Mapping[str, Any]]


def _log_rpc_success(method: Any, rid: Any) -> None:
    logger.info(
        "jsonrpc response method=%s id=%s status_code=%s",
        method,
        rid,
        200,
    )


def _log_rpc_error(method: Any, rid: Any, code: int, message: str) -> None:
    logger.info(
        "jsonrpc response method=%s id=%s status_code=%s error_code=%s error_message=%s",
        method,
        rid,
        _RPC_TO_HTTP.get(code, 500),
        code,
        message,
    )


def _request_obj_to_mapping(obj: RPCRequest | Mapping[str, Any]) -> Mapping[str, Any]:
    """Convert endpoint payload objects to the mapping expected by dispatcher."""
    if isinstance(obj, RPCRequest):
        return obj.model_dump()
    if isinstance(obj, Mapping):
        return obj
    raise HTTPException(status_code=400, detail="Invalid Request")


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
    has_id = "id" in obj
    rid = obj.get("id") if has_id else None
    method = obj.get("method")

    def _rpc_error(code: int, message: str, data: Any | None = None) -> Dict[str, Any]:
        _log_rpc_error(method, rid, code, message)
        return _err(code, message, rid, data)

    try:
        # Basic JSON-RPC validation
        if not isinstance(obj, Mapping):
            return _rpc_error(-32600, "Invalid Request")  # not an object
        # Be lenient: default to 2.0 when "jsonrpc" is omitted
        if obj.get("jsonrpc", "2.0") != "2.0":
            return _rpc_error(-32600, "Invalid Request")
        method = obj.get("method")
        if not isinstance(method, str) or "." not in method:
            return _rpc_error(-32601, "Method not found")

        model_name, alias = method.split(".", 1)
        model = resolve_model(api, model_name)
        if model is None:
            return _rpc_error(-32601, f"Unknown model '{model_name}'")

        by_alias = getattr(getattr(model, "ops", None), "by_alias", {}) or {}
        if alias not in by_alias:
            return _rpc_error(-32601, f"Method not found: {model_name}.{alias}")

        # Params
        try:
            params = _normalize_params(obj.get("params"))
        except HTTPException as exc:
            code, msg, data = http_exc_to_rpc(exc)
            return _rpc_error(code, msg, data)

        target = resolve_target(model, alias)
        payload = _coerce_payload(params)
        _reject_wrapper_keys(
            payload, allowed_keys=_allowed_wrapper_keys(model, alias, target)
        )
        if target == "bulk_delete" and not isinstance(payload, Mapping):
            payload = {"ids": payload}
        if not (
            target.startswith("bulk_")
            and target != "bulk_delete"
            and isinstance(payload, Sequence)
            and not isinstance(payload, (str, bytes, Mapping))
        ):
            norm_payload = _validate_input(model, alias, target, payload)
            if isinstance(payload, Mapping) and isinstance(norm_payload, Mapping):
                merged_payload = dict(payload)
                merged_payload.update(norm_payload)
                payload = merged_payload
            else:
                payload = norm_payload

        # Enforce auth when required
        if getattr(api, "_authn", None):
            method_id = f"{model.__name__}.{alias}"
            allow = getattr(api, "_allow_anon_ops", set())
            user = _user_from_request(request)
            if method_id not in allow and user is None:
                raise HTTPException(status_code=401, detail="Unauthorized")

        # Authorize (auth dep may already have raised; user may be on request.state)
        _authorize(api, request, model, alias, payload, _user_from_request(request))

        # Execute through unified transport dispatcher
        result = await dispatch_operation(
            api=api,
            request=request,
            db=db,
            model_or_name=model,
            alias=alias,
            target=target,
            payload=payload,
            rpc_id=rid,
            rpc_mode=True,
            response_serializer=lambda r: _rpc_serialize_output(
                model, alias, target, r
            ),
        )
        if not has_id:
            _log_rpc_success(method, None)
            return None
        _log_rpc_success(method, rid)
        return _ok(result, rid)

    except HTTPException as exc:
        code, msg, data = http_exc_to_rpc(exc)
        return _rpc_error(code, msg, data)
    except Exception:
        logger.exception("jsonrpc dispatch failed")
        # Internal error (per JSON-RPC); do not leak details
        return _rpc_error(-32603, ERROR_MESSAGES.get(-32603, "Internal error"))


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

    If `get_db` is provided, it will be used as a ASGI
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
                        api=api,
                        request=request,
                        db=db,
                        obj=_request_obj_to_mapping(item),
                    )
                    if resp is not None:
                        responses.append(resp)
                return JSONResponse(
                    content=responses,
                )
            elif isinstance(body, (RPCRequest, Mapping)):
                resp = await _dispatch_one(
                    api=api,
                    request=request,
                    db=db,
                    obj=_request_obj_to_mapping(body),
                )
                if resp is None:
                    return Response(status_code=204)
                return JSONResponse(
                    content=resp,
                )
            else:
                err = _err(-32600, "Invalid Request", None)
                return JSONResponse(content=err)

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
                        api=api,
                        request=request,
                        db=db,
                        obj=_request_obj_to_mapping(item),
                    )
                    if resp is not None:
                        responses.append(resp)
                return JSONResponse(
                    content=responses,
                )
            elif isinstance(body, (RPCRequest, Mapping)):
                resp = await _dispatch_one(
                    api=api,
                    request=request,
                    db=db,
                    obj=_request_obj_to_mapping(body),
                )
                if resp is None:
                    return Response(status_code=204)
                return JSONResponse(
                    content=resp,
                )
            else:
                err = _err(-32600, "Invalid Request", None)
                return JSONResponse(content=err)

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
                        api=api,
                        request=request,
                        db=db,
                        obj=_request_obj_to_mapping(item),
                    )
                    if resp is not None:
                        responses.append(resp)
                return JSONResponse(
                    content=responses,
                )
            elif isinstance(body, (RPCRequest, Mapping)):
                resp = await _dispatch_one(
                    api=api,
                    request=request,
                    db=db,
                    obj=_request_obj_to_mapping(body),
                )
                if resp is None:
                    return Response(status_code=204)
                return JSONResponse(
                    content=resp,
                )
            else:
                err = _err(-32600, "Invalid Request", None)
                return JSONResponse(content=err)

    else:
        # No dependencies; attempt to read db (and user) from request.state
        async def _endpoint(request: Request, body: Any = Body(...)):
            db = getattr(request.state, "db", None)
            if isinstance(body, list):
                responses: List[Dict[str, Any]] = []
                for item in body:
                    resp = await _dispatch_one(
                        api=api,
                        request=request,
                        db=db,
                        obj=_request_obj_to_mapping(item),
                    )
                    if resp is not None:
                        responses.append(resp)
                return JSONResponse(
                    content=responses,
                )
            elif isinstance(body, (RPCRequest, Mapping)):
                resp = await _dispatch_one(
                    api=api,
                    request=request,
                    db=db,
                    obj=_request_obj_to_mapping(body),
                )
                if resp is None:
                    return Response(status_code=204)
                return JSONResponse(
                    content=resp,
                )
            else:
                err = _err(-32600, "Invalid Request", None)
                return JSONResponse(content=err)

    async def _options_endpoint(request: Request):
        allow = "OPTIONS,POST"
        headers: Dict[str, str] = {
            "allow": allow,
            "access-control-allow-methods": allow,
        }

        origin = request.headers.get("origin")
        if origin:
            headers["access-control-allow-origin"] = origin
            headers["vary"] = "origin"

        req_headers = request.headers.get("access-control-request-headers")
        if req_headers:
            headers["access-control-allow-headers"] = req_headers
            headers["vary"] = (
                "origin,access-control-request-headers"
                if origin
                else "access-control-request-headers"
            )

        return Response(status_code=204, headers=headers)

    # Attach a single JSON-RPC POST route. Mount prefix controls final path.
    router.add_api_route(
        path="",
        endpoint=_options_endpoint,
        methods=["OPTIONS"],
        name="jsonrpc_options",
        tags=list(tags) if tags else None,
        include_in_schema=False,
    )

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
    return router


__all__ = ["build_jsonrpc_router"]
