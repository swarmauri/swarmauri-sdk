from __future__ import annotations

from typing import Any
from urllib.parse import quote

from ...response.stdapi import Response


TIGRBL_LENS_VERSION = "0.0.8"


def _with_leading_slash(path: str) -> str:
    return path if path.startswith("/") else f"/{path}"


def build_lens_html(router: Any, request: Any, *, spec_path: str) -> str:
    base = (getattr(request, "script_name", "") or "").rstrip("/")
    spec_url = f"{base}{_with_leading_slash(spec_path)}"
    quoted_spec_url = quote(spec_url, safe="/:?=&%")
    return f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{router.title} — Lens</title>
    <link
      rel="stylesheet"
      href="https://esm.sh/@tigrbljs/tigrbl-lens@{TIGRBL_LENS_VERSION}/dist/tigrbl-lens.css"
    />
    <style>
      html, body, #root {{
        margin: 0;
        width: 100%;
        min-height: 100%;
      }}
      body {{
        min-height: 100vh;
      }}
    </style>
  </head>
  <body>
    <div id="root"></div>
    <script type="importmap">
      {{
        "imports": {{
          "react": "https://esm.sh/react@19",
          "react-dom/client": "https://esm.sh/react-dom@19/client",
          "@tigrbljs/tigrbl-lens": "https://esm.sh/@tigrbljs/tigrbl-lens@{TIGRBL_LENS_VERSION}"
        }}
      }}
    </script>
    <script type="module">
      import React from "react";
      import {{ createRoot }} from "react-dom/client";
      import Lens from "@tigrbljs/tigrbl-lens";

      const rootEl = document.getElementById("root");
      if (rootEl) {{
        createRoot(rootEl).render(
          React.createElement(
            React.StrictMode,
            null,
            React.createElement(Lens, {{ url: "{quoted_spec_url}" }}),
          ),
        );
      }}
    </script>
  </body>
</html>
"""


def mount_lens(
    router: Any,
    *,
    path: str = "/lens",
    name: str = "__lens__",
    spec_path: str | None = None,
) -> Any:
    """Mount a tigrbl-lens HTML endpoint onto ``router``."""

    resolved_spec_path = spec_path or "/openrpc.json"

    def _lens_handler(request: Any) -> Response:
        return Response.html(
            build_lens_html(router, request, spec_path=resolved_spec_path)
        )

    router.add_api_route(
        path,
        _lens_handler,
        methods=["GET"],
        name=name,
        include_in_schema=False,
    )
    return router


__all__ = ["build_lens_html", "mount_lens"]
