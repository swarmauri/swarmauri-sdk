"""FastAPI app serving the Customer Success Command Center example."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from layout_engine_atoms.runtime.vue import create_layout_app

from .manifest import create_manifest


def create_app() -> FastAPI:
    manifest_app = create_layout_app(
        manifest_builder=create_manifest,
        mount_path="/customer-success",
    )
    asgi_app = manifest_app.asgi_app()

    fastapi = FastAPI()

    @fastapi.get("/")
    async def root() -> HTMLResponse:
        html = """
        <!doctype html>
        <html lang="en">
          <head>
            <meta charset="utf-8" />
            <title>Customer Success Command Center</title>
            <link rel="preconnect" href="https://fonts.googleapis.com" />
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
            <link
              href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
              rel="stylesheet"
            />
          </head>
          <body style="margin:0;background:#f4fffb;color:#113a3a;">
            <div id="app"></div>
            <script type="module">
              import { createLayoutApp } from "/customer-success/layout-engine-vue.es.js";

              const controller = createLayoutApp({
                manifestUrl: "/customer-success/manifest.json",
                target: "#app",
                initialPageId: "overview",
                onPageChange(pageId, page) {
                  console.debug("Customer Success page", pageId, page?.label);
                },
              });

              window.customerSuccessController = controller;
            </script>
          </body>
        </html>
        """
        return HTMLResponse(html)

    @fastapi.get("/customer-success/{path:path}")
    async def dashboard_assets(path: str) -> HTMLResponse:
        async def receive() -> dict[str, Any]:
            return {"type": "http.request", "body": b"", "more_body": False}

        messages: list[dict[str, Any]] = []

        async def send(message: dict[str, Any]) -> None:
            messages.append(message)

        scope = {
            "type": "http",
            "method": "GET",
            "path": f"/customer-success/{path}",
            "raw_path": f"/customer-success/{path}".encode(),
            "query_string": b"",
            "root_path": "",
            "scheme": "http",
            "http_version": "1.1",
            "headers": [],
        }
        await asgi_app(scope, receive, send)

        status = next(
            msg["status"] for msg in messages if msg["type"] == "http.response.start"
        )
        headers = {
            k.decode("latin-1"): v.decode("latin-1")
            for msg in messages
            if msg["type"] == "http.response.start"
            for (k, v) in msg.get("headers", [])
        }
        body = b"".join(
            msg.get("body", b"")
            for msg in messages
            if msg["type"] == "http.response.body"
        )
        return HTMLResponse(content=body, status_code=status, headers=headers)

    return fastapi


app = create_app()

__all__ = ["app", "create_app"]
