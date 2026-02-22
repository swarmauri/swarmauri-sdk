from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence

from ...runtime.status import ERROR_MESSAGES, _RPC_TO_HTTP, http_exc_to_rpc
from ...runtime.status.exceptions import HTTPException
from ...security.dependencies import Depends
from ...transport import JSONResponse, Request, Response
from ...transport.dispatcher import dispatch_operation, resolve_operation
from ...core.crud.params import Body
from ...router._router import Router
from ...bindings.rpc import _serialize_output
from .helpers import _err, _normalize_deps, _normalize_params, _ok
from .models import RPCRequest, RPCResponse

logger = logging.getLogger(__name__)


def _log_rpc_success(method: Any, rid: Any) -> None:
    logger.info("jsonrpc response method=%s id=%s status_code=%s", method, rid, 200)


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
    if isinstance(obj, RPCRequest):
        return obj.model_dump()
    if isinstance(obj, Mapping):
        return obj
    raise HTTPException(status_code=400, detail="Invalid Request")


async def _dispatch_one(
    *, router: Any, request: Request, db: Any, obj: Mapping[str, Any]
) -> Optional[Dict[str, Any]]:
    has_id = "id" in obj
    rid = obj.get("id") if has_id else None
    method = obj.get("method")

    def _rpc_error(code: int, message: str, data: Any | None = None) -> Dict[str, Any]:
        _log_rpc_error(method, rid, code, message)
        return _err(code, message, rid, data)

    try:
        if obj.get("jsonrpc", "2.0") != "2.0":
            return _rpc_error(-32600, "Invalid Request")
        if not isinstance(method, str) or "." not in method:
            return _rpc_error(-32601, "Method not found")

        model_name, alias = method.split(".", 1)
        try:
            resolution = resolve_operation(
                router=router, model_or_name=model_name, alias=alias
            )
        except LookupError:
            return _rpc_error(-32601, f"Unknown model '{model_name}'")

        params = _normalize_params(obj.get("params"))
        base_ctx: Dict[str, Any] = {}
        extra_ctx = getattr(request.state, "ctx", None)
        if isinstance(extra_ctx, Mapping):
            base_ctx.update(extra_ctx)
        base_ctx.setdefault("rpc_id", rid)

        result = await dispatch_operation(
            router=router,
            model_or_name=resolution.model,
            alias=alias,
            payload=params,
            db=db,
            request=request,
            ctx=base_ctx,
            response_serializer=lambda r: _serialize_output(
                resolution.model,
                alias,
                resolution.target,
                r,
            ),
            rpc_mode=True,
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
        return _rpc_error(-32603, ERROR_MESSAGES.get(-32603, "Internal error"))


def build_jsonrpc_router(
    router: Any,
    *,
    get_db: Optional[Callable[..., Any]] = None,
    tags: Sequence[str] | None = ("rpc",),
) -> Router:
    extra_router_deps = _normalize_deps(getattr(router, "rpc_dependencies", None))
    api_router = Router(dependencies=extra_router_deps or None)

    if get_db is not None:

        async def _endpoint(
            request: Request,
            body: RPCRequest | list[RPCRequest] = Body(...),
            db: Any = Depends(get_db),
        ):
            return await _handle_body(router=router, request=request, db=db, body=body)

    else:

        async def _endpoint(request: Request, body: Any = Body(...)):
            db = getattr(request.state, "db", None)
            return await _handle_body(router=router, request=request, db=db, body=body)

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

    api_router.add_route(
        path="",
        endpoint=_options_endpoint,
        methods=["OPTIONS"],
        name="jsonrpc_options",
        tags=list(tags) if tags else None,
        include_in_schema=False,
    )
    api_router.add_route(
        path="",
        endpoint=_endpoint,
        methods=["POST"],
        name="jsonrpc",
        tags=list(tags) if tags else None,
        summary="JSONRPC",
        description="JSON-RPC 2.0 endpoint.",
        response_model=RPCResponse | list[RPCResponse],
    )
    return api_router


async def _handle_body(
    *, router: Any, request: Request, db: Any, body: Any
) -> Response:
    if isinstance(body, list):
        responses: List[Dict[str, Any]] = []
        for item in body:
            resp = await _dispatch_one(
                router=router, request=request, db=db, obj=_request_obj_to_mapping(item)
            )
            if resp is not None:
                responses.append(resp)
        return JSONResponse(content=responses)

    if isinstance(body, (RPCRequest, Mapping)):
        resp = await _dispatch_one(
            router=router, request=request, db=db, obj=_request_obj_to_mapping(body)
        )
        if resp is None:
            return Response(status_code=204)
        return JSONResponse(content=resp)

    return JSONResponse(content=_err(-32600, "Invalid Request", None))


__all__ = ["build_jsonrpc_router"]
