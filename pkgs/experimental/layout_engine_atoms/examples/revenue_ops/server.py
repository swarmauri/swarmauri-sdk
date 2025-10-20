"""FastAPI app showcasing the Revenue Ops Command Center example."""

from __future__ import annotations

import asyncio
import contextlib
from collections import deque
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from layout_engine.events.ws import EventRouter, InProcEventBus
from layout_engine_atoms.runtime.vue import ManifestApp, ManifestEventsConfig

from .manifest import create_manifest

INCIDENT_TOPIC = "incidents/live"


def create_app() -> FastAPI:
    bus = InProcEventBus()
    router = EventRouter(bus)
    incident_history: deque[dict[str, Any]] = deque(maxlen=50)

    async def on_client_event(payload: dict[str, Any], ws) -> bool:
        topic = payload.get("topic")
        if topic == "incidents/ack":
            bus.publish(
                INCIDENT_TOPIC,
                {
                    "type": "acknowledged",
                    "tile_id": payload.get("payload", {}).get("tile_id"),
                    "by": payload.get("payload", {}).get("user"),
                },
            )
            return True
        if payload.get("type") == "manifest.patch":
            bus.publish(
                "manifest",
                {"type": "manifest.patch", "patch": payload.get("patch", {})},
                retain=True,
            )
            return True
        return False

    manifest_app = ManifestApp(
        manifest_builder=create_manifest,
        mount_path="/dashboard",
        events=ManifestEventsConfig(
            bus=bus,
            router=router,
            topics=("manifest", INCIDENT_TOPIC),
            replay_last=True,
            on_client_event=on_client_event,
        ),
    )

    asgi_app = manifest_app.asgi_app()

    fastapi = FastAPI()
    fastapi.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @fastapi.get("/")
    async def root() -> HTMLResponse:
        html = """
        <!doctype html>
        <html lang="en">
          <head>
            <meta charset="utf-8" />
            <title>Revenue Ops Command Center</title>
            <link rel="preconnect" href="https://fonts.googleapis.com" />
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
            <link
              href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
              rel="stylesheet"
            />
          </head>
          <body style="margin:0;background:#050a18;color:#f5f7ff;">
            <div id="app"></div>
            <script type="module">
              import { createLayoutApp } from "/dashboard/layout-engine-vue.es.js";

              const controller = createLayoutApp({
                manifestUrl: "/dashboard/manifest.json",
                target: "#app",
                events: {
                  onMessage(message) {
                    if (message.topic === "incidents/live") {
                      console.log("Incident stream", message.payload);
                    }
                  },
                },
              });

              controller.registerPlugin({
                afterUpdate(ctx) {
                  console.debug("Manifest updated", ctx.state.manifest?.version);
                },
              });
            </script>
          </body>
        </html>
        """
        return HTMLResponse(html)

    @fastapi.get("/dashboard/{path:path}")
    async def dashboard_assets(path: str):
        async def receive():
            return {"type": "http.request", "body": b"", "more_body": False}

        messages: list[dict[str, Any]] = []

        async def send(message: dict[str, Any]) -> None:
            messages.append(message)

        scope = {
            "type": "http",
            "method": "GET",
            "path": f"/dashboard/{path}",
            "raw_path": f"/dashboard/{path}".encode(),
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
        headers = dict(
            (k.decode("latin-1"), v.decode("latin-1"))
            for msg in messages
            if msg["type"] == "http.response.start"
            for (k, v) in msg.get("headers", [])
        )
        body = b"".join(
            msg.get("body", b"")
            for msg in messages
            if msg["type"] == "http.response.body"
        )
        return HTMLResponse(content=body, status_code=status, headers=headers)

    async def incident_stream() -> None:
        seq = 0
        while True:
            await asyncio.sleep(12)
            seq += 1
            incident = {
                "account": f"Trial Cohort {seq}",
                "owner": "Automation",
                "severity": "Medium",
                "opened": "moments ago",
            }
            incident_history.append(incident)
            bus.publish(
                INCIDENT_TOPIC,
                {
                    "type": "table:update",
                    "rows": list(incident_history),
                    "added": incident,
                },
                retain=True,
            )

    @fastapi.on_event("startup")
    async def start_background_tasks() -> None:
        fastapi.state.incident_task = asyncio.create_task(incident_stream())

    @fastapi.on_event("shutdown")
    async def stop_background_tasks() -> None:
        task: asyncio.Task | None = getattr(fastapi.state, "incident_task", None)
        if task:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task

    return fastapi


app = create_app()

__all__ = ["app", "create_app"]
