from __future__ import annotations

import asyncio
import contextlib
import json
from typing import Any, List

import pytest

from layout_engine.events.ws import EventRouter, InProcEventBus
from layout_engine_atoms.runtime.vue import ManifestApp, ManifestEventsConfig


async def _run_asgi(app, scope, queue: asyncio.Queue[dict], sent: List[dict]) -> None:
    async def receive() -> dict:
        return await queue.get()

    async def send(message: dict) -> None:
        sent.append(message)

    await app(scope, receive, send)


@pytest.mark.asyncio
async def test_websocket_bridge_with_event_bus() -> None:
    class TrackingBus(InProcEventBus):
        def __init__(self) -> None:
            super().__init__()
            self.subscribed: List[str] = []

        def subscribe(self, topic: str, fn, *, replay_last: bool = False):
            self.subscribed.append(topic)
            return super().subscribe(topic, fn, replay_last=replay_last)

    bus = TrackingBus()
    router = EventRouter(bus)

    manifest = {
        "kind": "layout_manifest",
        "grid": {"columns": [], "gap_x": 0, "gap_y": 0, "row_height": 1},
        "tiles": [],
        "viewport": {"width": 1, "height": 1},
        "version": "test",
    }

    app = ManifestApp(
        manifest_builder=lambda: manifest,
        events=ManifestEventsConfig(bus=bus, router=router, topics=("demo",)),
        mount_path="/dashboard",
    )

    asgi = app.asgi_app()

    scope = {
        "type": "websocket",
        "path": "/dashboard/events",
        "scheme": "ws",
        "method": "GET",
        "query_string": b"",
        "headers": [],
    }

    sent: List[dict[str, Any]] = []
    inbound: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
    await inbound.put({"type": "websocket.connect"})

    task = asyncio.create_task(_run_asgi(asgi, scope, inbound, sent))

    for _ in range(20):
        if any(msg.get("type") == "websocket.accept" for msg in sent):
            break
        await asyncio.sleep(0.05)

    assert any(msg.get("type") == "websocket.accept" for msg in sent)
    assert "demo" in bus.subscribed

    client_message = json.dumps(
        {"topic": "demo", "payload": {"source": "client"}, "retain": False}
    )
    await inbound.put({"type": "websocket.receive", "text": client_message})
    await inbound.put({"type": "websocket.disconnect", "code": 1000})

    await asyncio.sleep(0.1)
    if not task.done():
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task

    accept_messages = [msg for msg in sent if msg["type"] == "websocket.accept"]
    assert accept_messages, "websocket was not accepted"
