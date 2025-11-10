from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Mapping, MutableMapping, Sequence

from fastapi import FastAPI, WebSocket, WebSocketDisconnect


RealtimePublisher = Callable[["WebsocketMuxHub"], Awaitable[None]]


@dataclass(slots=True)
class RealtimeChannel:
    """Declarative manifest channel description."""

    id: str
    scope: str = "site"
    topic: str | None = None
    description: str | None = None
    meta: Mapping[str, Any] | None = None

    def as_manifest(self) -> dict[str, Any]:
        """Return a manifest-ready payload."""

        payload: dict[str, Any] = {
            "id": self.id,
            "scope": self.scope,
        }
        if self.topic:
            payload["topic"] = self.topic
        if self.description:
            payload["description"] = self.description
        if self.meta:
            payload["meta"] = dict(self.meta)
        return payload


@dataclass(slots=True)
class RealtimeOptions:
    """Configuration for websocket mux routing."""

    path: str = "/ws/events"
    channels: Sequence[RealtimeChannel] = ()
    publishers: Sequence[RealtimePublisher] = ()
    auto_subscribe: bool = True
    bindings: Sequence["RealtimeBinding"] = ()


class WebsocketMuxHub:
    """Minimal mux-compatible hub that manages websocket subscribers."""

    def __init__(self, *, path: str) -> None:
        self.path = path
        self._subscriptions: dict[WebSocket, set[str]] = {}
        self._lock = asyncio.Lock()
        self._publisher_tasks: list[asyncio.Task[Any]] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._subscriptions[websocket] = set()

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            self._subscriptions.pop(websocket, None)

    async def disconnect_all(self) -> None:
        async with self._lock:
            websockets = list(self._subscriptions.keys())
        for websocket in websockets:
            await self.disconnect(websocket)

    async def subscribe(self, websocket: WebSocket, channel: str) -> None:
        async with self._lock:
            if websocket not in self._subscriptions:
                self._subscriptions[websocket] = {channel}
            else:
                self._subscriptions[websocket].add(channel)

    async def unsubscribe(self, websocket: WebSocket, channel: str) -> None:
        async with self._lock:
            channels = self._subscriptions.get(websocket)
            if not channels:
                return
            channels.discard(channel)
            if not channels:
                self._subscriptions.pop(websocket, None)

    async def broadcast(self, channel: str, payload: Mapping[str, Any]) -> None:
        message = {"channel": channel, "payload": dict(payload)}
        async with self._lock:
            targets = [
                websocket
                for websocket, channels in self._subscriptions.items()
                if channel in channels
            ]
        stale: list[WebSocket] = []
        for websocket in targets:
            try:
                await websocket.send_json(message)
            except Exception:
                stale.append(websocket)
        for websocket in stale:
            await self.disconnect(websocket)

    async def start_publishers(self, publishers: Sequence[RealtimePublisher]) -> None:
        """Launch background publisher coroutines."""

        if not publishers:
            return
        loop = asyncio.get_running_loop()
        for publisher in publishers:
            task = loop.create_task(publisher(self))
            self._publisher_tasks.append(task)

    async def stop_publishers(self) -> None:
        for task in self._publisher_tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        self._publisher_tasks.clear()

    def mount(self, app: FastAPI, route_path: str) -> None:
        """Register the websocket route on the FastAPI app."""

        async def _endpoint(websocket: WebSocket) -> None:
            await self.connect(websocket)
            try:
                while True:
                    message = await websocket.receive_json()
                    action = message.get("action")
                    channel = message.get("channel")
                    if action == "subscribe" and isinstance(channel, str):
                        await self.subscribe(websocket, channel)
                    elif action == "unsubscribe" and isinstance(channel, str):
                        await self.unsubscribe(websocket, channel)
                    elif action == "publish" and isinstance(channel, str):
                        payload = message.get("payload") or {}
                        if isinstance(payload, Mapping):
                            await self.broadcast(channel, payload)
            except WebSocketDisconnect:
                await self.disconnect(websocket)

        app.add_api_websocket_route(route_path, _endpoint)


@dataclass(slots=True)
class RealtimeBinding:
    """Declarative mapping between a channel payload and a tile's props."""

    channel: str
    tile_id: str
    fields: Mapping[str, str] = field(default_factory=dict)

    def as_payload(self) -> MutableMapping[str, Any]:
        return {
            "channel": self.channel,
            "tileId": self.tile_id,
            "fields": dict(self.fields),
        }
