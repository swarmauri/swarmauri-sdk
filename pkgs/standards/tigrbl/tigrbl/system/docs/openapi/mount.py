from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from ...._concrete._response import Response
from ...._spec.binding_spec import HttpRestBindingSpec
from ...._spec.op_spec import OpSpec
from tigrbl_concrete._mapping.model_helpers import _OpSpecGroup
from .schema import openapi


def _register_runtime_openapi_op(router: Any, *, path: str, alias: str) -> None:
    """Ensure the kernel can resolve the OpenAPI endpoint as a runtime operation."""
    tables = getattr(router, "tables", None)
    if not isinstance(tables, dict):
        return

    model_name = "__tigrbl_system_docs__"
    model = tables.get(model_name)
    if model is None:
        model = type("TigrblSystemDocs", (), {})
        model.resource_name = "system_docs"
        model.hooks = SimpleNamespace()
        model.ops = SimpleNamespace(by_alias={}, all=())
        model.opspecs = SimpleNamespace(all=())
        tables[model_name] = model

    op = OpSpec(
        alias=alias,
        target="read",
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

    async def _runtime_openapi_step(ctx: Any) -> None:
        payload = openapi(router)
        setattr(ctx, "result", payload)
        if isinstance(getattr(ctx, "temp", None), dict):
            ctx.temp.setdefault("egress", {})["result"] = payload

    async def _suppress_transport_send(ctx: Any) -> None:
        temp = getattr(ctx, "temp", None)
        if isinstance(temp, dict):
            temp.setdefault("egress", {})["suppress_asgi_send"] = True

    hooks_ns = getattr(model.hooks, alias, None)
    if hooks_ns is None:
        hooks_ns = SimpleNamespace()
        setattr(model.hooks, alias, hooks_ns)
    hooks_ns.HANDLER = [_runtime_openapi_step]
    hooks_ns.POST_COMMIT = [_suppress_transport_send]


def mount_openapi(
    router: Any,
    *,
    path: str = "/openapi.json",
    name: str = "__openapi__",
) -> Any:
    """Mount an OpenAPI JSON endpoint onto ``router``."""

    def _openapi_handler(request: Any) -> Response:
        return Response.json(openapi(router))

    _register_runtime_openapi_op(router, path=path, alias=name)

    router.add_route(
        path,
        _openapi_handler,
        methods=["GET"],
        name=name,
        include_in_schema=False,
    )
    return router


__all__ = ["mount_openapi"]
