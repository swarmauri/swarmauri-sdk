"""Thin Vue runtime for layout-engine manifests with optional realtime events."""

from __future__ import annotations

import asyncio
import contextlib
import json
import mimetypes
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import (
    Any,
    Awaitable,
    Callable,
    Iterable,
    Mapping,
    MutableMapping,
    Sequence,
)
from urllib.parse import parse_qs

from layout_engine import Manifest
from layout_engine.manifest import manifest_to_json
from layout_engine.events.ws import EventRouter, InProcEventBus

ManifestBuilder = Callable[[], Manifest | Mapping[str, Any]]


class ManifestWebSocket:
    """Convenience wrapper around ASGI websocket messages."""

    def __init__(self, scope, receive, send):
        self.scope = scope
        self._receive = receive
        self._send = send
        self.accepted = False
        self.closed = False
        self.close_code: int | None = None
        self._query_params: Mapping[str, list[str]] | None = None

    @property
    def path(self) -> str:
        return self.scope.get("path", "")

    @property
    def query_params(self) -> Mapping[str, list[str]]:
        if self._query_params is None:
            raw = self.scope.get("query_string", b"")
            if isinstance(raw, bytes):
                raw = raw.decode("latin-1")
            self._query_params = parse_qs(raw)
        return self._query_params

    async def accept(
        self,
        *,
        headers: Iterable[tuple[str, str]] | None = None,
        subprotocol: str | None = None,
    ) -> None:
        if self.accepted:
            return
        message: dict[str, Any] = {"type": "websocket.accept"}
        if headers:
            message["headers"] = [
                (name.encode("latin-1"), value.encode("latin-1"))
                for name, value in headers
            ]
        if subprotocol:
            message["subprotocol"] = subprotocol
        await self._send(message)
        self.accepted = True

    async def receive(self) -> str | bytes | None:
        message = await self._receive()
        mtype = message.get("type")
        if mtype == "websocket.receive":
            if message.get("text") is not None:
                return message["text"]
            return message.get("bytes")
        if mtype == "websocket.disconnect":
            self.closed = True
            self.close_code = message.get("code")
            return None
        return None

    async def receive_json(self) -> Any:
        payload = await self.receive()
        if payload is None:
            return None
        if isinstance(payload, bytes):
            payload = payload.decode("utf-8")
        try:
            return json.loads(payload)
        except json.JSONDecodeError:
            return None

    async def send_text(self, data: str) -> None:
        if self.closed:
            return
        await self._send({"type": "websocket.send", "text": data})

    async def send_json(self, data: Any) -> None:
        await self.send_text(json.dumps(data))

    async def close(self, code: int = 1000, reason: str | None = None) -> None:
        if self.closed and self.close_code == code:
            return
        message: dict[str, Any] = {"type": "websocket.close", "code": code}
        if reason:
            message["reason"] = reason
        await self._send(message)
        self.closed = True
        self.close_code = code


@dataclass
class ManifestEventsConfig:
    """Configuration for websocket event streaming."""

    route: str | None = None
    bus: InProcEventBus | None = None
    router: EventRouter | None = None
    topics: Sequence[str] | None = None
    replay_last: bool = True
    on_client_event: (
        Callable[[dict, ManifestWebSocket], Awaitable[bool | None] | bool | None] | None
    ) = None
    on_connect: Callable[[ManifestWebSocket], Awaitable[None]] | None = None
    on_disconnect: Callable[[ManifestWebSocket], Awaitable[None]] | None = None
    heartbeat_interval: float | None = None

    def __post_init__(self) -> None:
        if self.router and not self.bus:
            self.bus = self.router.bus
        if self.topics is None:
            self.topics = ()


def _ensure_prefixed(path: str) -> str:
    if not path.startswith("/"):
        path = f"/{path}"
    return path


def _ensure_trailing_slash(path: str) -> str:
    if path != "/" and not path.endswith("/"):
        path = f"{path}/"
    return path


def _guess_mimetype(filename: str) -> str:
    if filename.endswith(".html"):
        return "text/html; charset=utf-8"
    if filename.endswith(".css"):
        return "text/css; charset=utf-8"
    if filename.endswith(".js"):
        return "application/javascript; charset=utf-8"
    if filename.endswith(".json"):
        return "application/json; charset=utf-8"
    mimetype, _ = mimetypes.guess_type(filename)
    if mimetype and mimetype.startswith("text/"):
        return f"{mimetype}; charset=utf-8"
    return mimetype or "application/octet-stream"


def load_client_assets(root: Path | None = None) -> dict[str, bytes]:
    """Return packaged client assets for the Vue runtime."""

    client_root = Path(__file__).resolve().parent / "client"
    core_root = client_root.parent.parent / "core"
    sources: list[Path] = []
    if root is not None:
        sources.append(root)
    else:
        dist_root = client_root / "dist"
        if dist_root.exists():
            sources.append(dist_root)
        sources.append(client_root)

    assets: dict[str, bytes] = {}
    for base in sources:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_file():
                relative_key = path.relative_to(base).as_posix()
                assets.setdefault(relative_key, path.read_bytes())

    if core_root.exists():
        for path in core_root.rglob("*.js"):
            if path.is_file():
                relative_key = Path("core") / path.relative_to(core_root)
                assets.setdefault(relative_key.as_posix(), path.read_bytes())

    return assets


@dataclass
class ManifestApp:
    """Serve manifests, static assets, and optional event streams."""

    manifest_builder: ManifestBuilder
    mount_path: str = "/"
    catalog: str = "vue"
    static_assets: Mapping[str, bytes] | None = None
    manifest_route: str | None = None
    index_asset: str = "index.html"
    extra_headers: Iterable[tuple[str, str]] = field(default_factory=tuple)
    events: ManifestEventsConfig | None = None

    def __post_init__(self) -> None:
        self.mount_path = _ensure_trailing_slash(_ensure_prefixed(self.mount_path))
        if self.manifest_route is None:
            self.manifest_route = f"{self.mount_path.rstrip('/')}/manifest.json"
        else:
            self.manifest_route = _ensure_prefixed(self.manifest_route)

        if self.events:
            if self.events.route:
                self.events.route = _ensure_prefixed(self.events.route)
            else:
                base = self.mount_path.rstrip("/") or "/"
                self.events.route = f"{base}/events"

    @cached_property
    def assets(self) -> Mapping[str, bytes]:
        if self.static_assets is not None:
            return self.static_assets
        return load_client_assets()

    def build_manifest_payload(self) -> MutableMapping[str, Any]:
        manifest = self.manifest_builder()
        if isinstance(manifest, Manifest):
            manifest_json = manifest_to_json(manifest)
            payload: MutableMapping[str, Any] = json.loads(manifest_json)
            return payload
        if isinstance(manifest, Mapping):
            return dict(manifest)
        raise TypeError(
            "manifest_builder must return layout_engine.Manifest or mapping, "
            f"got {type(manifest)!r}"
        )

    def _manifest_response(self) -> tuple[int, list[tuple[str, str]], bytes]:
        payload = self.build_manifest_payload()
        body = json.dumps(payload).encode("utf-8")
        headers = [
            ("content-type", "application/json; charset=utf-8"),
            ("cache-control", "no-cache, no-store, must-revalidate"),
        ]
        headers.extend((k.lower(), v) for k, v in self.extra_headers)
        return 200, headers, body

    def _asset_response(
        self, asset_path: str
    ) -> tuple[int, list[tuple[str, str]], bytes]:
        assets = self.assets
        if asset_path.startswith("/"):
            asset_path = asset_path[1:]
        asset_path = asset_path or self.index_asset
        if asset_path not in assets:
            return 404, [("content-type", "text/plain; charset=utf-8")], b"Not Found"
        headers = [
            ("content-type", _guess_mimetype(asset_path)),
            ("cache-control", "no-cache, no-store, must-revalidate"),
        ]
        headers.extend((k.lower(), v) for k, v in self.extra_headers)
        return 200, headers, assets[asset_path]

    async def _handle_websocket(self, scope, receive, send) -> None:
        events_cfg = self.events
        ws = ManifestWebSocket(scope, receive, send)
        if not events_cfg:
            await ws.close(code=4404)
            return

        await ws.accept()
        loop = asyncio.get_running_loop()
        unsubscribers: list[Callable[[], None]] = []
        heartbeat_task: asyncio.Task[None] | None = None

        async def send_outbound(payload: Any, topic: str | None = None) -> None:
            if ws.closed:
                return
            message = payload
            if (
                topic is not None
                and isinstance(payload, Mapping)
                and "topic" not in payload
            ):
                message = {"topic": topic, "payload": payload}
            await ws.send_json(message)

        def subscribe_to_topic(topic: str, replay: bool) -> None:
            if not events_cfg.bus:
                return

            def _subscriber(message: dict) -> None:
                if ws.closed:
                    return
                loop.create_task(send_outbound(message, topic=topic))

            unsub = events_cfg.bus.subscribe(topic, _subscriber, replay_last=replay)
            unsubscribers.append(unsub)

        try:
            if events_cfg.on_connect:
                await events_cfg.on_connect(ws)

            if events_cfg.bus and events_cfg.topics:
                for topic in events_cfg.topics:
                    subscribe_to_topic(topic, events_cfg.replay_last)

            if events_cfg.heartbeat_interval:
                heartbeat_task = asyncio.create_task(
                    self._heartbeat(ws, events_cfg.heartbeat_interval)
                )

            while True:
                incoming = await ws.receive()
                if incoming is None:
                    break

                data = None
                if isinstance(incoming, bytes):
                    try:
                        data = json.loads(incoming.decode("utf-8"))
                    except json.JSONDecodeError:
                        continue
                else:
                    try:
                        data = json.loads(incoming)
                    except json.JSONDecodeError:
                        continue

                handled = False
                if events_cfg.on_client_event:
                    result = events_cfg.on_client_event(data, ws)
                    if asyncio.iscoroutine(result):
                        result = await result
                    handled = bool(result)

                if not handled and events_cfg.router:
                    try:
                        events_cfg.router.dispatch(data)
                        handled = True
                    except Exception:
                        handled = False

                if not handled and events_cfg.bus and isinstance(data, Mapping):
                    topic = data.get("topic")
                    if topic:
                        payload = data.get("payload", data)
                        retain = bool(data.get("retain"))
                        if not isinstance(payload, dict):
                            payload = data
                        events_cfg.bus.publish(topic, payload, retain=retain)
                        handled = True

            if not ws.closed:
                await ws.close(code=1000)
        finally:
            for unsub in unsubscribers:
                with contextlib.suppress(Exception):
                    unsub()
            if heartbeat_task:
                heartbeat_task.cancel()
                with contextlib.suppress(Exception):
                    await heartbeat_task
            if events_cfg and events_cfg.on_disconnect:
                await events_cfg.on_disconnect(ws)

    async def _heartbeat(self, ws: ManifestWebSocket, interval: float) -> None:
        while not ws.closed:
            await asyncio.sleep(interval)
            if ws.closed:
                break
            try:
                await ws.send_json({"type": "heartbeat"})
            except Exception:
                break

    def asgi_app(self):
        """Return an ASGI application that serves manifests, assets, and events."""

        async def app(scope, receive, send):
            scope_type = scope.get("type")

            if scope_type == "websocket":
                events_cfg = self.events
                path = scope.get("path", "")
                route = events_cfg.route if events_cfg else None
                if events_cfg and route and path.rstrip("/") == route.rstrip("/"):
                    await self._handle_websocket(scope, receive, send)
                else:
                    await send({"type": "websocket.close", "code": 4404})
                return

            if scope_type != "http":
                await send(
                    {
                        "type": "http.response.start",
                        "status": 404,
                        "headers": [(b"content-type", b"text/plain; charset=utf-8")],
                    }
                )
                await send(
                    {
                        "type": "http.response.body",
                        "body": b"Not Found",
                        "more_body": False,
                    }
                )
                return

            method = scope.get("method", "GET").upper()
            if method not in {"GET", "HEAD"}:
                await send(
                    {
                        "type": "http.response.start",
                        "status": 405,
                        "headers": [(b"content-type", b"text/plain; charset=utf-8")],
                    }
                )
                await send(
                    {
                        "type": "http.response.body",
                        "body": b"Method Not Allowed",
                        "more_body": False,
                    }
                )
                return

            path = scope.get("path", "")
            if path == self.mount_path.rstrip("/") and not path.endswith("/"):
                await send(
                    {
                        "type": "http.response.start",
                        "status": 307,
                        "headers": [
                            (b"location", f"{self.mount_path}".encode("latin-1"))
                        ],
                    }
                )
                await send(
                    {
                        "type": "http.response.body",
                        "body": b"",
                        "more_body": False,
                    }
                )
                return

            if path == self.manifest_route:
                status, headers, body = self._manifest_response()
            elif path.startswith(self.mount_path):
                asset_path = path[len(self.mount_path) :]
                status, headers, body = self._asset_response(asset_path)
            else:
                status, headers, body = (
                    404,
                    [("content-type", "text/plain; charset=utf-8")],
                    b"Not Found",
                )

            await send(
                {
                    "type": "http.response.start",
                    "status": status,
                    "headers": [
                        (k.encode("latin-1"), v.encode("latin-1")) for k, v in headers
                    ],
                }
            )
            if method == "HEAD":
                body = b""
            await send({"type": "http.response.body", "body": body, "more_body": False})

        return app


def create_layout_app(
    *,
    manifest_builder: ManifestBuilder,
    mount_path: str = "/",
    **options: Any,
) -> ManifestApp:
    """Create a :class:`ManifestApp` pre-configured with bundled Vue assets.

    Parameters
    ----------
    manifest_builder:
        Callable that returns a layout manifest (dict or ``layout_engine.Manifest``).
    mount_path:
        Base path where the app should be served (defaults to ``"/"``).
    **options:
        Additional keyword arguments forwarded to :class:`ManifestApp`.
    """

    return ManifestApp(
        manifest_builder=manifest_builder, mount_path=mount_path, **options
    )


__all__ = [
    "ManifestApp",
    "ManifestBuilder",
    "ManifestEventsConfig",
    "ManifestWebSocket",
    "create_layout_app",
    "load_client_assets",
]
