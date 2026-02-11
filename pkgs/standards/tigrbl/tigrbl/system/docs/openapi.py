from __future__ import annotations

from typing import Any

from ...deps._stdapi_types import Request, Response


def mount_openapi(router: Any, *, path: str | None = None) -> Any:
    openapi_path = path or getattr(router, "openapi_url", "/openapi.json")

    def _openapi_handler(request: Request) -> Response:
        return Response.json(router.openapi())

    router.add_api_route(
        openapi_path,
        _openapi_handler,
        methods=["GET"],
        name="__openapi__",
        include_in_schema=False,
    )
    return router


__all__ = ["mount_openapi"]
