from __future__ import annotations

from typing import Any

from ...deps._stdapi_types import Request, Response


def mount_lens(
    router: Any, *, path: str = "/lens", spec_url: str = "/openrpc.json"
) -> Any:
    def _lens_handler(request: Request) -> Response:
        return Response.html(render_lens_html(request, router, spec_url=spec_url))

    router.add_api_route(
        path,
        _lens_handler,
        methods=["GET"],
        name="__lens__",
        include_in_schema=False,
    )
    return router


def render_lens_html(
    request: Request, router: Any, *, spec_url: str = "/openrpc.json"
) -> str:
    base = (request.script_name or "").rstrip("/")
    resolved_spec_url = spec_url if spec_url.startswith("/") else f"/{spec_url}"
    spec_href = f"{base}{resolved_spec_url}"
    title = getattr(router, "title", "API")

    return f"""<!doctype html>
<html>
  <head>
    <meta charset=\"utf-8\" />
    <title>{title} — Lens</title>
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <style>
      body {{ font-family: sans-serif; margin: 2rem; }}
      pre {{ background: #111827; color: #e5e7eb; padding: 1rem; border-radius: 0.5rem; }}
      a {{ color: #2563eb; }}
    </style>
  </head>
  <body>
    <h1>{title} Lens</h1>
    <p>OpenRPC document: <a href=\"{spec_href}\">{spec_href}</a></p>
    <pre>Use this endpoint with your preferred OpenRPC visualization tooling.</pre>
  </body>
</html>
"""


__all__ = ["mount_lens", "render_lens_html"]
