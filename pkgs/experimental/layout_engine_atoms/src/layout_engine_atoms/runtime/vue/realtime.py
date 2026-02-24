from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Mapping, MutableMapping, Sequence

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

RealtimePublisher = Callable[["WebsocketMuxHub"], Awaitable[None]]
WebSocketAuthHandler = Callable[[WebSocket], Awaitable[bool]]


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
    auth_handler: WebSocketAuthHandler | None = None
    max_subscriptions_per_client: int = 100


class WebsocketMuxHub:
    """Minimal mux-compatible hub that manages websocket subscribers.

    Args:
        path: WebSocket endpoint path
        auth_handler: Optional async function to authenticate WebSocket connections.
            Should return True to allow connection, False to reject.
        max_subscriptions_per_client: Maximum number of channels a single client
            can subscribe to (default: 100)
    """

    def __init__(
        self,
        *,
        path: str,
        auth_handler: WebSocketAuthHandler | None = None,
        max_subscriptions_per_client: int = 100,
    ) -> None:
        self.path = path
        self.auth_handler = auth_handler
        self.max_subscriptions_per_client = max_subscriptions_per_client
        self._subscriptions: dict[WebSocket, set[str]] = {}
        self._lock = asyncio.Lock()
        self._publisher_tasks: list[asyncio.Task[Any]] = []

    async def connect(self, websocket: WebSocket) -> None:
        """Connect a WebSocket client with optional authentication.

        Args:
            websocket: The WebSocket connection to authenticate and accept

        Raises:
            WebSocketDisconnect: If authentication fails
        """
        # Authenticate if handler is provided
        if self.auth_handler:
            try:
                is_authorized = await self.auth_handler(websocket)
                if not is_authorized:
                    logger.warning(
                        f"WebSocket authentication failed for client: "
                        f"{websocket.client}"
                    )
                    await websocket.close(code=1008, reason="Unauthorized")
                    raise WebSocketDisconnect(code=1008, reason="Unauthorized")
            except Exception as e:
                logger.error(f"Authentication error: {e}", exc_info=True)
                await websocket.close(code=1011, reason="Authentication error")
                raise WebSocketDisconnect(code=1011, reason="Authentication error")

        await websocket.accept()
        async with self._lock:
            self._subscriptions[websocket] = set()

        logger.info(f"WebSocket connected: {websocket.client}")

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            self._subscriptions.pop(websocket, None)

    async def disconnect_all(self) -> None:
        async with self._lock:
            websockets = list(self._subscriptions.keys())
        for websocket in websockets:
            await self.disconnect(websocket)

    async def subscribe(self, websocket: WebSocket, channel: str) -> None:
        """Subscribe a WebSocket client to a channel.

        Args:
            websocket: The WebSocket connection
            channel: The channel ID to subscribe to

        Raises:
            ValueError: If subscription limit is exceeded
        """
        async with self._lock:
            if websocket not in self._subscriptions:
                self._subscriptions[websocket] = {channel}
            else:
                current_subs = self._subscriptions[websocket]
                if len(current_subs) >= self.max_subscriptions_per_client:
                    logger.warning(
                        f"Client {websocket.client} exceeded subscription limit "
                        f"({self.max_subscriptions_per_client})"
                    )
                    # Send error message to client
                    await websocket.send_json({
                        "error": "Subscription limit exceeded",
                        "limit": self.max_subscriptions_per_client
                    })
                    return
                current_subs.add(channel)

        logger.debug(f"Client {websocket.client} subscribed to channel: {channel}")

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
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected during broadcast: {websocket.client}")
                stale.append(websocket)
            except Exception as e:
                logger.error(
                    f"Failed to send message to WebSocket {websocket.client}: {e}"
                )
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
