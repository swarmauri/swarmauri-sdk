from __future__ import annotations

from typing import Any

from tigrbl_concrete._concrete._response import Response
from tigrbl_concrete.system.docs.runtime_ops import register_runtime_get_route
from .schema import openapi


def _register_runtime_openapi_op(router: Any, *, path: str, alias: str) -> None:
    """Ensure the kernel can resolve the OpenAPI endpoint as a runtime operation."""

    def _openapi_runtime_handler(_request: Any) -> Response:
        return Response.json(openapi(router))

    register_runtime_get_route(
        router,
        path=path,
        alias=alias,
        endpoint=_openapi_runtime_handler,
    )


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
