"""Simple ASGI app serving the Svelte runtime bundle."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from layout_engine.events.ws import InProcEventBus, EventRouter
from layout_engine_atoms.runtime.svelte import (
    ManifestEventsConfig,
    create_layout_app,
)

from .manifest import create_manifest


@lru_cache(maxsize=1)
def _manifest_app():
    events_bus = InProcEventBus()
    router = EventRouter(events_bus)

    manifest_app = create_layout_app(
        manifest_builder=create_manifest,
        mount_path="/svelte",
        events=ManifestEventsConfig(
            bus=events_bus,
            router=router,
            topics=("manifest",),
            replay_last=True,
        ),
    )
    return manifest_app.asgi_app()


def create_app() -> FastAPI:
    fastapi = FastAPI()
    asgi_app = _manifest_app()

    @fastapi.get("/")
    async def index() -> HTMLResponse:
        html = """
        <!doctype html>
        <html lang="en">
          <head>
            <meta charset="utf-8" />
            <title>Svelte Runtime Demo</title>
            <link rel="preconnect" href="https://fonts.googleapis.com" />
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
            <link
              href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
              rel="stylesheet"
            />
            <style>
              body { margin: 0; background: #050a18; color: #f6f7ff; }
            </style>
          </head>
          <body>
            <div id="app"></div>
            <script src="/svelte/layout-engine-svelte.umd.js"></script>
            <script>
              const { createLayoutApp } = window.LayoutEngineSvelte || {};
              if (!createLayoutApp) {
                console.error('Svelte runtime bundle failed to load.');
              } else {
                createLayoutApp({
                  manifestUrl: "/svelte/manifest.json",
                  target: "#app",
                  theme: { tokens: { accent: "#5ab1ff" } }
                });
              }
            </script>
          </body>
        </html>
        """
        return HTMLResponse(html)

    @fastapi.get("/svelte/{path:path}")
    async def svelte_assets(path: str):
        if not path:
            return await index()

        async def receive():
            return {"type": "http.request", "body": b"", "more_body": False}

        messages: list[dict[str, Any]] = []

        async def send(message: dict[str, Any]) -> None:
            messages.append(message)

        scope = {
            "type": "http",
            "method": "GET",
            "path": f"/svelte/{path}",
            "raw_path": f"/svelte/{path}".encode(),
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

__all__ = ["app"]
