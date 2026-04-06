from __future__ import annotations

from pathlib import Path
from typing import Any

from tigrbl_concrete._concrete._response import Response
from tigrbl_concrete.system.docs.runtime_ops import register_runtime_get_route

_DOCS_DIR = Path(__file__).resolve().parent
_SWAGGER_ASSETS = {
    "swagger-ui.css": ("text/css; charset=utf-8", _DOCS_DIR / "swagger-ui.css"),
    "swagger-ui-bundle.js": (
        "application/javascript; charset=utf-8",
        _DOCS_DIR / "swagger-ui-bundle.js",
    ),
    "swagger-ui-standalone-preset.js": (
        "application/javascript; charset=utf-8",
        _DOCS_DIR / "swagger-ui-standalone-preset.js",
    ),
}


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
    title = getattr(docs_owner, "title", getattr(router, "title", "API"))
    assets_path = "/system/docs/assets"
    return f"""<!doctype html>
<html>
  <head>
    <meta charset=\"utf-8\" />
    <title>{title} — API Docs</title>
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <link rel=\"stylesheet\" href=\"{assets_path}/swagger-ui.css\" />
    <style>
      .swagger-ui .topbar {{
        display: none;
      }}
    </style>
  </head>
  <body>
    <header style="font-family: sans-serif; padding: 16px 24px 8px;">
      <h1 style="margin: 0 0 6px;">{title} — Swagger UI</h1>
      <p style="margin: 0; color: #666;">
        If interactive docs do not load, fetch the OpenAPI spec at <code>{spec_url}</code>.
      </p>
    </header>
    <div id=\"swagger-ui\"></div>
    <script src=\"{assets_path}/swagger-ui-bundle.js\"></script>
    <script src=\"{assets_path}/swagger-ui-standalone-preset.js\"></script>
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


def _serve_swagger_asset(asset_name: str) -> Response:
    media_type, file_path = _SWAGGER_ASSETS[asset_name]
    payload = file_path.read_bytes()
    return Response(body=payload, media_type=media_type)


def _build_asset_endpoint(asset_name: str):
    def _endpoint(_request: Any) -> Response:
        return _serve_swagger_asset(asset_name)

    return _endpoint


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

    for asset_name in _SWAGGER_ASSETS:
        endpoint = _build_asset_endpoint(asset_name)
        asset_path = f"/system/docs/assets/{asset_name}"
        register_runtime_get_route(
            router,
            path=asset_path,
            alias=f"__docs_asset_{asset_name.replace('.', '_')}__",
            endpoint=endpoint,
        )
        router.add_route(
            asset_path,
            endpoint,
            methods=["GET"],
            name=f"__docs_asset_{asset_name.replace('.', '_')}__",
            include_in_schema=False,
        )
    return router


__all__ = ["build_swagger_html", "mount_swagger"]
