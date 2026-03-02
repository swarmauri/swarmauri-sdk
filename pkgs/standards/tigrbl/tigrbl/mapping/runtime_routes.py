from __future__ import annotations

import inspect
from dataclasses import replace
from types import SimpleNamespace
from typing import Any, Callable

from .._spec.binding_spec import HttpRestBindingSpec
from .._spec.op_spec import OpSpec
from ..core.crud.params import Param
from ..mapping.core_resolver import (
    annotation_marker,
    extract_param_value,
    is_request_annotation,
    split_annotated,
)
from ..runtime.atoms.dep.extra import invoke_dependency as invoke_extra_dependency
from ..security.dependencies import Dependency


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


def _make_runtime_dep_store(name: str, dep: Callable[..., Any]) -> Callable[..., Any]:
    async def _dep_store(request: Any) -> None:
        router = getattr(request, "app", None)
        if router is None:
            return
        value = await invoke_extra_dependency(router, dep, request)
        _runtime_route_kwargs_store(request)[name] = value

    return _dep_store


def _planned_route_deps(route: Any, handler: Callable[..., Any]) -> tuple[Any, ...]:
    deps: list[Any] = list(tuple(getattr(route, "dependencies", ()) or ()))

    for name, param in inspect.signature(handler).parameters.items():
        base_annotation, extras = split_annotated(param.annotation)
        dep_marker = annotation_marker(extras, Dependency)
        if isinstance(param.default, Dependency):
            deps.append(_make_runtime_dep_store(name, param.default.dependency))
        elif dep_marker is not None:
            deps.append(_make_runtime_dep_store(name, dep_marker.dependency))

    return tuple(deps)


def _planned_route_secdeps(route: Any) -> tuple[Any, ...]:
    return tuple(getattr(route, "security_dependencies", ()) or ())


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

        if is_request_annotation(base_annotation) or name == "request":
            kwargs[name] = request
            continue

        if (
            isinstance(param.default, Dependency)
            or annotation_marker(extras, Dependency) is not None
        ):
            # Dependency values are populated by PRE_TX_BEGIN dep atoms.
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


async def invoke_runtime_route_handler(
    ctx: Any,
    *,
    handler: Callable[..., Any],
) -> None:
    request = getattr(ctx, "request", None)
    kwargs = _resolve_handler_kwargs(handler, request)
    result = handler(**kwargs)
    if inspect.isawaitable(result):
        result = await result

    temp = _ensure_temp(ctx)
    egress = temp.setdefault("egress", {}) if isinstance(temp, dict) else {}
    if hasattr(result, "status_code") and hasattr(result, "body"):
        headers_obj = getattr(result, "headers", None)
        if hasattr(headers_obj, "items"):
            headers_obj = dict(headers_obj.items())
        response = {
            "status_code": int(getattr(result, "status_code", 200) or 200),
            "headers": dict(headers_obj or {}),
            "body": getattr(result, "body", b""),
        }
        egress["transport_response"] = response
        egress["suppress_asgi_send"] = True
        return

    setattr(ctx, "result", result)
    egress["result"] = result


def _merge_table_op_binding(route: Any) -> bool:
    model = getattr(route, "tigrbl_model", None)
    alias = getattr(route, "tigrbl_alias", None)
    if not (isinstance(model, type) and isinstance(alias, str) and alias):
        return False

    specs = tuple(
        getattr(getattr(model, "ops", SimpleNamespace()), "by_alias", {}).get(alias, ())
        or ()
    )
    existing_spec = specs[0] if specs else None
    if existing_spec is None:
        return False

    path = getattr(route, "path_template", None)
    methods = tuple(getattr(route, "methods", ()) or ())
    if not (isinstance(path, str) and methods):
        return True

    mounted_binding = HttpRestBindingSpec(
        proto="http.rest",
        path=path,
        methods=tuple(str(method).upper() for method in methods),
    )
    merged_bindings = list(tuple(getattr(existing_spec, "bindings", ()) or ()))
    if mounted_binding not in merged_bindings:
        merged_bindings.append(mounted_binding)

    planned_deps = _planned_route_deps(route, getattr(route, "handler"))
    existing_deps = tuple(getattr(existing_spec, "deps", ()) or ())
    merged_deps = tuple(existing_deps) + tuple(
        dep for dep in planned_deps if dep not in existing_deps
    )

    planned_secdeps = _planned_route_secdeps(route)
    existing_secdeps = tuple(getattr(existing_spec, "secdeps", ()) or ())
    merged_secdeps = tuple(existing_secdeps) + tuple(
        dep for dep in planned_secdeps if dep not in existing_secdeps
    )

    updated_spec = replace(
        existing_spec,
        bindings=tuple(merged_bindings),
        deps=merged_deps,
        secdeps=merged_secdeps,
    )
    model.ops.by_alias[alias] = (updated_spec,)
    model.opspecs.all = tuple(
        spec
        for spec in tuple(getattr(getattr(model, "opspecs", None), "all", ()) or ())
        if getattr(spec, "alias", None) != alias
    ) + (updated_spec,)
    return True


def register_runtime_route(app: Any, route: Any) -> None:
    if _merge_table_op_binding(route):
        return

    path = getattr(route, "path_template", None)
    methods = tuple(getattr(route, "methods", ()) or ())
    handler = getattr(route, "handler", None)
    if not (isinstance(path, str) and methods and callable(handler)):
        return

    method_tokens = "_".join(sorted(str(m).lower() for m in methods))
    alias = f"__route__:{method_tokens}:{path}"
    model = app._ensure_system_route_model()

    op = OpSpec(
        alias=alias,
        target="read",
        arity="collection",
        persist="skip",
        expose_routes=False,
        bindings=(
            HttpRestBindingSpec(
                proto="http.rest",
                path=path,
                methods=tuple(str(method).upper() for method in methods),
            ),
        ),
        deps=_planned_route_deps(route, handler),
        secdeps=_planned_route_secdeps(route),
    )
    model.ops.by_alias[alias] = (op,)
    model.opspecs.all = tuple(
        spec for spec in model.opspecs.all if getattr(spec, "alias", None) != alias
    ) + (op,)

    async def _runtime_route_handler(ctx: Any) -> None:
        await invoke_runtime_route_handler(ctx, handler=handler)

    hooks_ns = getattr(model.hooks, alias, None)
    if hooks_ns is None:
        hooks_ns = SimpleNamespace()
        setattr(model.hooks, alias, hooks_ns)
    hooks_ns.HANDLER = [_runtime_route_handler]


__all__ = ["invoke_runtime_route_handler", "register_runtime_route"]
