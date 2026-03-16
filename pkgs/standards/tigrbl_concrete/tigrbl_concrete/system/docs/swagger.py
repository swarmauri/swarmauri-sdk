from __future__ import annotations

from typing import Any

from tigrbl_concrete._concrete._response import Response
from tigrbl_concrete.system.docs.runtime_ops import register_runtime_get_route


def _resolve_docs_owner(target: Any) -> Any:
    """Resolve the object that carries OpenAPI and Swagger metadata."""

    owner = getattr(target, "router", None)
    return owner if owner is not None else target


def build_swagger_html(router: Any, request: Any) -> str:
    docs_owner = _resolve_docs_owner(router)
    base = (getattr(request, "script_name", "") or "").rstrip("/")
    openapi_path = getattr(docs_owner, "openapi_url", "/openapi.json")
    openapi_url = openapi_path if openapi_path.startswith("/") else f"/{openapi_path}"
    spec_url = f"{base}{openapi_url}"
    version = getattr(docs_owner, "swagger_ui_version", "5.31.0")
    title = getattr(docs_owner, "title", getattr(router, "title", "API"))
    return f"""<!doctype html>
<html>
  <head>
    <meta charset=\"utf-8\" />
    <title>{title} — API Docs</title>
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <link rel=\"stylesheet\" href=\"https://unpkg.com/swagger-ui-dist@{version}/swagger-ui.css\" />
    <style>
      .swagger-ui .topbar {{
        display: none;
      }}
    </style>
  </head>
  <body>
    <div id=\"swagger-ui\"></div>
    <script src=\"https://unpkg.com/swagger-ui-dist@{version}/swagger-ui-bundle.js\"></script>
    <script src=\"https://unpkg.com/swagger-ui-dist@{version}/swagger-ui-standalone-preset.js\"></script>
    <script>
      window.onload = function () {{
        window.ui = SwaggerUIBundle({{
          url: \"{spec_url}\",
          dom_id: \"#swagger-ui\",
          presets: [
            SwaggerUIBundle.presets.apis,
            SwaggerUIStandalonePreset
          ],
          layout: \"StandaloneLayout\"
        }});
      }};
    </script>
  </body>
</html>
"""


def mount_swagger(
    router: Any,
    *,
    path: str = "/docs",
    name: str = "__docs__",
) -> Any:
    """Mount a Swagger UI HTML endpoint onto ``router``."""

    def _docs_handler(request: Any) -> Response:
        return Response.html(build_swagger_html(router, request))

    register_runtime_get_route(
        router,
        path=path,
        alias=name,
        endpoint=_docs_handler,
    )

    router.add_route(
        path,
        _docs_handler,
        methods=["GET"],
        name=name,
        include_in_schema=False,
    )
    return router


__all__ = ["build_swagger_html", "mount_swagger"]
