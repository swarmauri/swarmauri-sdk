from __future__ import annotations

from typing import Any

from ...responses import Response


def build_swagger_html(router: Any, request: Any) -> str:
    base = (getattr(request, "script_name", "") or "").rstrip("/")
    openapi_url = (
        router.openapi_url
        if router.openapi_url.startswith("/")
        else f"/{router.openapi_url}"
    )
    spec_url = f"{base}{openapi_url}"
    version = router.swagger_ui_version
    return f"""<!doctype html>
<html>
  <head>
    <meta charset=\"utf-8\" />
    <title>{router.title} — API Docs</title>
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

    router.add_route(
        path,
        _docs_handler,
        methods=["GET"],
        name=name,
        include_in_schema=False,
    )
    return router


__all__ = ["build_swagger_html", "mount_swagger"]
