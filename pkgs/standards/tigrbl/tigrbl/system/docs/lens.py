from __future__ import annotations

from typing import Any

from ...deps._stdapi_types import Response


def build_lens_html(router: Any, request: Any) -> str:
    base = (getattr(request, "script_name", "") or "").rstrip("/")
    openapi_url = (
        router.openapi_url
        if router.openapi_url.startswith("/")
        else f"/{router.openapi_url}"
    )
    spec_url = f"{base}{openapi_url}"
    return f"""<!doctype html>
<html>
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>{router.title} — Lens</title>
    <script id=\"api-reference\" data-url=\"{spec_url}\"></script>
    <script src=\"https://cdn.jsdelivr.net/npm/@scalar/api-reference\"></script>
  </head>
  <body></body>
</html>
"""


def mount_lens(
    router: Any,
    *,
    path: str = "/lens",
    name: str = "__lens__",
) -> Any:
    """Mount a Scalar Lens HTML endpoint onto ``router``."""

    def _lens_handler(request: Any) -> Response:
        return Response.html(build_lens_html(router, request))

    router.add_api_route(
        path,
        _lens_handler,
        methods=["GET"],
        name=name,
        include_in_schema=False,
    )
    return router


__all__ = ["build_lens_html", "mount_lens"]
