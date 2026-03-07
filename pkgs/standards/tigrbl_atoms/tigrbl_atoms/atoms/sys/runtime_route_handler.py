from __future__ import annotations

from ...types import Atom, Ctx, OperatedCtx
from ...stages import Resolved, Operated

import inspect
from typing import Any, Callable

from ... import events as _ev
from ...gw.raw import GwRouteEnvelope
from ...status import StatusDetailError
from tigrbl_ops_oltp.crud.params import Param
from tigrbl_canon.mapping.core_resolver import (
    annotation_marker,
    extract_param_value,
    is_request_annotation,
    split_annotated,
)
from ...types import DependencyLike, is_dependency_like
from ..dep.extra import invoke_dependency as invoke_extra_dependency

ANCHOR = _ev.SYS_HANDLER_PERSISTENCE


def _ensure_temp(ctx: Any) -> dict[str, Any]:
    temp = getattr(ctx, "temp", None)
    if isinstance(temp, dict):
        return temp
    temp = {}
    setattr(ctx, "temp", temp)
    return temp


def _runtime_route_kwargs_store(request: Any) -> dict[str, Any]:
    state = getattr(request, "state", None)
    if state is None:
        return {}
    store = getattr(state, "_runtime_route_kwargs", None)
    if isinstance(store, dict):
        return store
    store = {}
    setattr(state, "_runtime_route_kwargs", store)
    return store


async def _resolve_runtime_deps(handler: Callable[..., Any], request: Any) -> None:
    app = getattr(request, "app", None)
    if app is None:
        return
    for name, param in inspect.signature(handler).parameters.items():
        base_annotation, extras = split_annotated(param.annotation)
        dep_marker = annotation_marker(extras, DependencyLike)
        dep = None
        if is_dependency_like(param.default):
            dep = param.default.dependency
        elif dep_marker is not None:
            dep = dep_marker.dependency
        if dep is None:
            continue
        value = await invoke_extra_dependency(app, dep, request)
        _runtime_route_kwargs_store(request)[name] = value


def _resolve_handler_kwargs(
    handler: Callable[..., Any], request: Any
) -> dict[str, Any]:
    kwargs: dict[str, Any] = {}
    injected = _runtime_route_kwargs_store(request)
    body_cache: Any | None = None

    for name, param in inspect.signature(handler).parameters.items():
        if name in injected:
            kwargs[name] = injected[name]
            continue

        base_annotation, extras = split_annotated(param.annotation)
        param_marker = annotation_marker(extras, Param)

        if (
            is_request_annotation(base_annotation)
            or name == "request"
            or name.lower().endswith("request")
        ):
            kwargs[name] = request
            continue

        if (
            is_dependency_like(param.default)
            or annotation_marker(extras, DependencyLike) is not None
        ):
            continue

        if isinstance(param.default, Param) or param_marker is not None:
            marker = param.default if isinstance(param.default, Param) else param_marker
            value, found = extract_param_value(marker, request, name, body_cache)
            if found:
                kwargs[name] = value
            elif not marker.required:
                kwargs[name] = marker.default
            continue

        if name in request.path_params:
            kwargs[name] = request.path_params[name]
        elif name in request.query_params:
            kwargs[name] = request.query_params[name]
        elif param.default is not inspect._empty:
            kwargs[name] = param.default

    return kwargs


async def _run(obj: object | None, ctx: Any) -> None:
    del obj
    temp = _ensure_temp(ctx)
    route = temp.setdefault("route", {})
    handler = route.get("handler") if isinstance(route, dict) else None

    if route.get("method_not_allowed") is True:
        raise StatusDetailError(status_code=405, detail="Method Not Allowed")
    if not callable(handler):
        raise StatusDetailError(
            status_code=404, detail="No runtime operation matched request."
        )

    request = getattr(ctx, "request", None)
    if request is None:
        request = getattr(ctx, "req", None)
    if request is None:
        raise StatusDetailError(
            status_code=500, detail="Runtime request context missing."
        )

    raw = getattr(ctx, "gw_raw", None)
    if raw is None:
        raw = getattr(ctx, "raw", None)
    if isinstance(raw, GwRouteEnvelope):
        request.path_params = dict(route.get("path_params") or {})
    elif route.get("path_params"):
        request.path_params = dict(route.get("path_params") or {})

    await _resolve_runtime_deps(handler, request)
    kwargs = _resolve_handler_kwargs(handler, request)

    result = handler(**kwargs)
    if inspect.isawaitable(result):
        result = await result

    if hasattr(result, "status_code") and hasattr(result, "body"):
        headers_obj = getattr(result, "headers", None)
        if hasattr(headers_obj, "items"):
            headers_obj = dict(headers_obj.items())
        egress = temp.setdefault("egress", {})
        egress["transport_response"] = {
            "status_code": int(getattr(result, "status_code", 200) or 200),
            "headers": dict(headers_obj or {}),
            "body": getattr(result, "body", b""),
        }
        return

    setattr(ctx, "result", result)


class AtomImpl(Atom[Resolved, Operated]):
    name = "sys.runtime_route_handler"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Resolved]) -> Ctx[Operated]:
        await _run(obj, ctx)
        return ctx.promote(OperatedCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
