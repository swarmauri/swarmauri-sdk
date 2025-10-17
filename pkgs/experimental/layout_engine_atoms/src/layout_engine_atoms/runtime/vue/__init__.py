"""Thin Vue runtime for layout-engine manifests."""

from __future__ import annotations

import json
import mimetypes
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, MutableMapping, Optional

from layout_engine import Manifest
from layout_engine.manifest import manifest_to_json


ManifestBuilder = Callable[[], Manifest | Mapping[str, Any]]


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
    return assets


@dataclass
class ManifestApp:
    """Serve manifests and bundled Vue assets via a minimal ASGI app.

    Args:
        manifest_builder: Callable returning a :class:`Manifest` or manifest dict.
        mount_path: URL prefix where the Vue bundle is exposed (default ``/``).
        catalog: Name of the atom catalog being advertised (default ``vue``).
        static_assets: Optional mapping ``path -> bytes``. When omitted the
            packaged assets from :func:`load_client_assets` are used.
        manifest_route: Overrides the manifest URL (defaults to
            ``{mount_path}manifest.json``).
        index_asset: Name of the asset served when the user requests the mount
            root (default ``index.html``).
    """

    manifest_builder: ManifestBuilder
    mount_path: str = "/"
    catalog: str = "vue"
    static_assets: Optional[Mapping[str, bytes]] = None
    manifest_route: Optional[str] = None
    index_asset: str = "index.html"
    extra_headers: Iterable[tuple[str, str]] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        self.mount_path = _ensure_trailing_slash(_ensure_prefixed(self.mount_path))
        if self.manifest_route is None:
            self.manifest_route = f"{self.mount_path.rstrip('/')}/manifest.json"
        else:
            self.manifest_route = _ensure_prefixed(self.manifest_route)

    @cached_property
    def assets(self) -> Mapping[str, bytes]:
        if self.static_assets is not None:
            return self.static_assets
        return load_client_assets()

    def build_manifest_payload(self) -> MutableMapping[str, Any]:
        """Return the manifest payload as a mutable dictionary."""
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
            ("cache-control", "public, max-age=31536000"),
        ]
        headers.extend((k.lower(), v) for k, v in self.extra_headers)
        return 200, headers, assets[asset_path]

    def asgi_app(self):
        """Return an ASGI application that serves the manifest and static assets."""

        async def app(scope, receive, send):
            if scope["type"] != "http":
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
            # Support mount path without trailing slash (e.g., /dashboard)
            if path == self.mount_path.rstrip("/") and not path.endswith("/"):
                redirect_headers = [
                    (b"location", f"{self.mount_path}".encode("latin-1"))
                ]
                await send(
                    {
                        "type": "http.response.start",
                        "status": 307,
                        "headers": redirect_headers,
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


__all__ = ["ManifestApp", "ManifestBuilder", "load_client_assets"]
