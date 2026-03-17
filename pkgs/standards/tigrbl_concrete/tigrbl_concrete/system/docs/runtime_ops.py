from __future__ import annotations

import inspect
from types import SimpleNamespace
from typing import Any, Callable

from tigrbl_concrete._concrete._response import Response
from tigrbl_core._spec.binding_spec import HttpRestBindingSpec
from tigrbl_core._spec.op_spec import OpSpec
from tigrbl_concrete._mapping.model_helpers import _OpSpecGroup


def ensure_system_docs_model(router: Any) -> type | None:
    """Return the synthetic runtime model used for system documentation routes."""
    tables = getattr(router, "tables", None)
    if not isinstance(tables, dict):
        return None

    model_name = "__tigrbl_system_docs__"
    model = tables.get(model_name)
    if model is None:
        model = type("TigrblSystemDocs", (), {})
        model.resource_name = "system_docs"
        model.hooks = SimpleNamespace()
        model.ops = SimpleNamespace(by_alias={}, all=())
        model.opspecs = SimpleNamespace(all=())
        tables[model_name] = model
    return model


def register_runtime_get_route(
    router: Any,
    *,
    path: str,
    alias: str,
    endpoint: Callable[..., Any],
) -> None:
    """Register a GET-only route endpoint as a runtime operation."""
    model = ensure_system_docs_model(router)
    if model is None:
        return

    op = OpSpec(
        alias=alias,
        target="__runtime__",
        arity="collection",
        persist="skip",
        expose_routes=False,
        expose_rpc=False,
        bindings=(HttpRestBindingSpec(proto="http.rest", path=path, methods=("GET",)),),
    )
    model.ops.by_alias[alias] = _OpSpecGroup((op,))
    model.opspecs.all = tuple(
        spec for spec in model.opspecs.all if getattr(spec, "alias", None) != alias
    ) + (op,)

    async def _runtime_route_step(ctx: Any) -> None:
        request = getattr(ctx, "request", None)
        try:
            response = endpoint(request)
        except TypeError:
            response = endpoint()
        if inspect.isawaitable(response):
            response = await response

        if isinstance(response, Response):
            payload = {
                "status_code": int(getattr(response, "status_code", 200) or 200),
                "headers": dict(getattr(response, "headers", ()) or ()),
                "body": getattr(response, "body", b""),
            }
            temp = getattr(ctx, "temp", None)
            if isinstance(temp, dict):
                temp.setdefault("route", {})["short_circuit"] = True
                temp.setdefault("egress", {})["transport_response"] = payload
                temp["egress"]["suppress_asgi_send"] = True
            setattr(ctx, "transport_response", payload)
            return

        setattr(ctx, "result", response)
        temp = getattr(ctx, "temp", None)
        if isinstance(temp, dict):
            temp.setdefault("egress", {})["result"] = response

    hooks_ns = getattr(model.hooks, alias, None)
    if hooks_ns is None:
        hooks_ns = SimpleNamespace()
        setattr(model.hooks, alias, hooks_ns)
    hooks_ns.HANDLER = [_runtime_route_step]


__all__ = ["ensure_system_docs_model", "register_runtime_get_route"]
