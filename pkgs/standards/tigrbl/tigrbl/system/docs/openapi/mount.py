from __future__ import annotations

from typing import Any

from ....responses import Response
from .schema import openapi


def mount_openapi(
    router: Any,
    *,
    path: str = "/openapi.json",
    name: str = "__openapi__",
) -> Any:
    """Mount an OpenAPI JSON endpoint onto ``router``."""

    def _openapi_handler(request: Any) -> Response:
        return Response.json(openapi(router))

    router.add_api_route(
        path,
        _openapi_handler,
        methods=["GET"],
        name=name,
        include_in_schema=False,
    )
    return router


__all__ = ["mount_openapi"]
