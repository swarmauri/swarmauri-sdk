"""FastAPI app serving the SwarmaKit-only Svelte landing page demo."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from layout_engine.events.ws import EventRouter, InProcEventBus
from layout_engine_atoms.runtime.svelte import (
    ManifestEventsConfig,
    create_layout_app,
)

from .manifest import create_manifest

CLIENT_BUNDLE_DIR = (
    Path(__file__).resolve().parents[2]
    / "src"
    / "layout_engine_atoms"
    / "runtime"
    / "svelte"
    / "client"
    / "dist"
)
REQUIRED_ASSETS = ("layout-engine-svelte.es.js", "layout-engine-svelte.umd.js")


def _ensure_client_bundle() -> None:
    missing = [
        name for name in REQUIRED_ASSETS if not (CLIENT_BUNDLE_DIR / name).exists()
    ]
    if missing:
        formatted = "\n  ".join(missing)
        raise RuntimeError(
            "Svelte runtime assets are missing.\n"
            "Run `npm install` (first time) and `npm run build` inside\n"
            "  pkgs/experimental/layout_engine_atoms/src/layout_engine_atoms/runtime/svelte/client\n"
            "before launching the demo.\n"
            "Missing files:\n"
            f"  {formatted}"
        )


@lru_cache(maxsize=1)
def _manifest_app():
    _ensure_client_bundle()
    bus = InProcEventBus()
    router = EventRouter(bus)
    manifest_app = create_layout_app(
        manifest_builder=create_manifest,
        mount_path="/swarmakit-svelte",
        events=ManifestEventsConfig(
            bus=bus,
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
            <title>SwarmaKit Svelte Landing</title>
            <link rel="preconnect" href="https://fonts.googleapis.com" />
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
            <link
              href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
              rel="stylesheet"
            />
            <style>
              :root { color-scheme: dark; }
              body {
                margin: 0;
                background: #050512;
                color: #f3f4ff;
                font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
              }
            </style>
          </head>
          <body>
            <div id="app"></div>
            <script src="/swarmakit-svelte/layout-engine-svelte.umd.js"></script>
            <script>
              const runtime = window.LayoutEngineSvelte;
              if (!runtime?.createLayoutApp) {
                console.error("Svelte runtime bundle failed to load.");
              } else {
                const controller = runtime.createLayoutApp({
                  manifestUrl: "/swarmakit-svelte/manifest.json",
                  target: "#app",
                });
                controller.setTheme({
                  tokens: {
                    "color-surface": "#050512",
                    "color-surface-elevated": "rgba(20, 23, 51, 0.88)",
                    "color-text-primary": "#f3f4ff",
                    "color-text-muted": "rgba(201, 205, 255, 0.72)",
                    "color-accent": "#7c6cff",
                    "swarmakit-button-primary-bg": "#7c6cff",
                    "swarmakit-button-secondary-bg": "#1f1a3a",
                    "swarmakit-badge-status-bg": "#58d38c",
                    "swarmakit-toggle-track": "rgba(124,108,255,0.45)",
                    "swarmakit-toggle-track-active": "#7c6cff",
                  },
                });
                window.swarmakitSvelte = controller;
              }
            </script>
          </body>
        </html>
        """
        return HTMLResponse(html)

    @fastapi.get("/swarmakit-svelte/{path:path}")
    async def svelte_assets(path: str):
        if not path:
            return await index()

        async def receive() -> dict[str, Any]:
            return {"type": "http.request", "body": b"", "more_body": False}

        messages: list[dict[str, Any]] = []

        async def send(message: dict[str, Any]) -> None:
            messages.append(message)

        scope = {
            "type": "http",
            "method": "GET",
            "path": f"/swarmakit-svelte/{path}",
            "raw_path": f"/swarmakit-svelte/{path}".encode(),
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
