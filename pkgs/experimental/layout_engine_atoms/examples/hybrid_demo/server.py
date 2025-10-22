"""Hybrid demo showcasing SPA + MPA manifests with realtime updates."""

from __future__ import annotations

import asyncio
import contextlib
from collections import deque
from itertools import cycle
from typing import Any, Callable, Deque, Dict, Iterable

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from layout_engine.events.ws import EventRouter, InProcEventBus
from layout_engine_atoms.runtime.vue import ManifestEventsConfig, create_layout_app

from .manifest import SEED_INCIDENTS, create_mpa_manifest, create_spa_manifest
from .patches import MpaPatchBuilder, PatchBuilder


class RuntimeApp:
    def __init__(
        self,
        name: str,
        mount_path: str,
        manifest_factory: Callable[[], Dict[str, Any]],
        patch_builder: PatchBuilder,
        incidents: Iterable[Dict[str, str]],
    ) -> None:
        self.name = name
        self.manifest_factory = manifest_factory
        self.patch_builder = patch_builder
        self.history: Deque[Dict[str, str]] = deque(incidents, maxlen=12)
        self.bus = InProcEventBus()
        self.router = EventRouter(self.bus)
        self.app = create_layout_app(
            manifest_builder=self.manifest_factory,
            mount_path=mount_path,
            events=ManifestEventsConfig(
                bus=self.bus,
                router=self.router,
                topics=("manifest",),
                replay_last=True,
            ),
        )
        self.counter = len(self.history)
        self.statuses = cycle(
            [
                "Investigating automation alerts",
                "Waiting for customer reply",
                "Escalated to success pod",
                "Mitigated by automation",
            ]
        )
        self.owners = cycle(["Fernandez", "Lopez", "Singh", "Carson", "Idowu"])
        self._publish_initial()

    def _publish_initial(self) -> None:
        patch = self.patch_builder.build_patch(list(self.history))
        self.bus.publish(
            "manifest",
            {"type": "manifest.patch", "patch": patch},
            retain=True,
        )

    async def stream_incidents(self) -> None:
        while True:
            await asyncio.sleep(15)
            self.counter += 1
            self.history.appendleft(
                {
                    "account": f"Activation Cohort {self.counter}",
                    "owner": next(self.owners),
                    "status": next(self.statuses),
                    "updated": "moments ago",
                }
            )
            patch = self.patch_builder.build_patch(list(self.history))
            self.bus.publish(
                "manifest",
                {"type": "manifest.patch", "patch": patch},
                retain=True,
            )


def create_app() -> FastAPI:
    fastapi = FastAPI()

    spa_runtime = RuntimeApp(
        name="spa",
        mount_path="/hybrid-demo/spa",
        manifest_factory=create_spa_manifest,
        patch_builder=PatchBuilder(create_spa_manifest),
        incidents=SEED_INCIDENTS,
    )
    mpa_runtime = RuntimeApp(
        name="mpa",
        mount_path="/hybrid-demo/mpa",
        manifest_factory=create_mpa_manifest,
        patch_builder=MpaPatchBuilder(create_mpa_manifest),
        incidents=SEED_INCIDENTS,
    )

    fastapi.mount("/hybrid-demo/spa", spa_runtime.app.asgi_app())
    fastapi.mount("/hybrid-demo/mpa", mpa_runtime.app.asgi_app())

    runtimes = [spa_runtime, mpa_runtime]

    @fastapi.get("/hybrid-demo")
    async def landing() -> HTMLResponse:
        html = """
        <!doctype html>
        <html lang="en">
          <head>
            <meta charset="utf-8" />
            <title>Hybrid Layout Engine Demo</title>
            <style>
              body { font-family: Inter, system-ui, sans-serif; background:#060b1a; color:#f6f8ff; margin:0; }
              main { padding: 3rem 2rem; max-width: 960px; margin: 0 auto; }
              a { color: #5ab1ff; }
              section { margin-bottom: 2.5rem; }
            </style>
          </head>
          <body>
            <main>
              <h1>Hybrid Demo</h1>
              <p>Choose between a single-page (SPA) manifest and a multi-page (MPA) manifest. Both streams live incidents via the websocket bridge.</p>
              <section>
                <h2>Single-page Runtime</h2>
                <p><a href="/hybrid-demo/spa/" target="_blank">Open SPA dashboard</a></p>
              </section>
              <section>
                <h2>Multi-page Runtime</h2>
                <p><a href="/hybrid-demo/mpa/" target="_blank">Open MPA dashboard</a></p>
              </section>
              <section>
                <h2>Instructions</h2>
                <ul>
                  <li>Open DevTools &gt; Network &gt; WS to observe <code>/events</code> traffic.</li>
                  <li>Incidents table updates every ~15 seconds.</li>
                  <li>Use the primary/secondary buttons to navigate between pages in the MPA view.</li>
                </ul>
              </section>
            </main>
          </body>
        </html>
        """
        return HTMLResponse(html)

    @fastapi.on_event("startup")
    async def start_streams() -> None:
        fastapi.state.runtime_tasks = [
            asyncio.create_task(rt.stream_incidents()) for rt in runtimes
        ]

    @fastapi.on_event("shutdown")
    async def stop_streams() -> None:
        for task in getattr(fastapi.state, "runtime_tasks", []):
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task

    return fastapi


app = create_app()

__all__ = ["app", "create_app"]
