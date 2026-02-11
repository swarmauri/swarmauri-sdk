from __future__ import annotations

from typing import Any

from ...deps._stdapi_types import Request, Response


def mount_swagger(router: Any, *, path: str | None = None) -> Any:
    docs_path = path or getattr(router, "docs_url", "/docs")

    def _docs_handler(request: Request) -> Response:
        return Response.html(render_swagger_html(request, router))

    router.add_api_route(
        docs_path,
        _docs_handler,
        methods=["GET"],
        name="__docs__",
        include_in_schema=False,
    )
    return router


def render_swagger_html(request: Request, router: Any) -> str:
    base = (request.script_name or "").rstrip("/")
    openapi_url = getattr(router, "openapi_url", "/openapi.json")
    openapi_path = openapi_url if openapi_url.startswith("/") else f"/{openapi_url}"
    spec_url = f"{base}{openapi_path}"
    title = getattr(router, "title", "API")
    version = getattr(router, "swagger_ui_version", "5.31.0")

    return f"""<!doctype html>
<html>
  <head>
    <meta charset=\"utf-8\" />
    <title>{title} — API Docs</title>
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <link rel=\"stylesheet\" href=\"https://unpkg.com/swagger-ui-dist@{version}/swagger-ui.css\" />
  </head>
  <body>
    <div id=\"swagger-ui\"></div>
    <script src=\"https://unpkg.com/swagger-ui-dist@{version}/swagger-ui-bundle.js\"></script>
    <script src=\"https://unpkg.com/swagger-ui-dist@{version}/swagger-ui-standalone-preset.js\"></script>
    <script>
      window.onload = function () {{
        window.ui = SwaggerUIBundle({{
          url: "{spec_url}",
          dom_id: "#swagger-ui",
          presets: [
            SwaggerUIBundle.presets.apis,
            SwaggerUIStandalonePreset
          ],
          layout: "StandaloneLayout"
        }});
      }};
    </script>
  </body>
</html>
"""


__all__ = ["mount_swagger", "render_swagger_html"]
