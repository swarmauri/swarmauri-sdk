from __future__ import annotations

import asyncio
import json
from typing import Any, Tuple

import pytest

from layout_engine_atoms.runtime.vue import (
    ManifestApp,
    create_layout_app,
    load_client_assets,
)


async def _make_request(
    app, path: str, method: str = "GET"
) -> Tuple[int, list[tuple[str, str]], bytes]:
    messages: list[dict[str, Any]] = []

    async def send(message: dict[str, Any]) -> None:
        messages.append(message)

    async def receive() -> dict[str, Any]:
        return {"type": "http.request", "body": b"", "more_body": False}

    scope = {
        "type": "http",
        "method": method,
        "path": path,
        "raw_path": path.encode(),
        "query_string": b"",
        "root_path": "",
        "scheme": "http",
        "http_version": "1.1",
        "headers": [],
    }

    await app(scope, receive, send)

    start = next(msg for msg in messages if msg["type"] == "http.response.start")
    body = b"".join(
        msg.get("body", b"") for msg in messages if msg["type"] == "http.response.body"
    )
    headers = [
        (k.decode("latin-1"), v.decode("latin-1")) for k, v in start.get("headers", [])
    ]
    return start["status"], headers, body


@pytest.fixture
def sample_assets() -> dict[str, bytes]:
    return {
        "index.html": b"<html><body>index</body></html>",
        "app.js": b"console.log('demo');",
    }


@pytest.fixture
def manifest_app(sample_assets):
    manifest = {"kind": "layout_manifest", "version": "test"}

    app = ManifestApp(
        manifest_builder=lambda: manifest,
        mount_path="/dashboard",
        static_assets=sample_assets,
    )
    return app


def _request(
    app, path: str, method: str = "GET"
) -> Tuple[int, list[tuple[str, str]], bytes]:
    return asyncio.run(_make_request(app, path, method=method))


def test_manifest_route_returns_json(manifest_app):
    app = manifest_app.asgi_app()
    status, headers, body = _request(app, "/dashboard/manifest.json")
    assert status == 200
    assert ("content-type", "application/json; charset=utf-8") in headers
    payload = json.loads(body.decode())
    assert payload["kind"] == "layout_manifest"


def test_static_index_served_at_mount_root(manifest_app):
    app = manifest_app.asgi_app()
    status, headers, body = _request(app, "/dashboard/")
    assert status == 200
    assert ("content-type", "text/html; charset=utf-8") in headers
    assert body.startswith(b"<html>")


def test_static_asset_served(manifest_app):
    app = manifest_app.asgi_app()
    status, headers, body = _request(app, "/dashboard/app.js")
    assert status == 200
    assert ("content-type", "application/javascript; charset=utf-8") in headers
    assert body.endswith(b";")


def test_missing_asset_returns_404(manifest_app):
    app = manifest_app.asgi_app()
    status, headers, body = _request(app, "/dashboard/missing.js")
    assert status == 404
    assert body == b"Not Found"


def test_head_request_has_empty_body(manifest_app):
    app = manifest_app.asgi_app()
    status, headers, body = _request(app, "/dashboard/manifest.json", method="HEAD")
    assert status == 200
    assert body == b""


def test_build_manifest_payload_from_mapping(manifest_app):
    payload = manifest_app.build_manifest_payload()
    assert payload["kind"] == "layout_manifest"


def test_load_client_assets_includes_dist_bundle():
    assets = load_client_assets()
    bundle_names = set(assets)
    assert any(name.endswith("layout-engine-vue.es.js") for name in bundle_names), (
        "expected ESM bundle in packaged client assets"
    )
    assert "core/index.js" in bundle_names, (
        "expected core module entry exposed for browser runtime"
    )


def test_manifest_app_serves_packaged_bundle():
    manifest = {"kind": "layout_manifest", "version": "bundle-test"}

    app = ManifestApp(
        manifest_builder=lambda: manifest,
        mount_path="/dashboard",
    ).asgi_app()

    status, headers, body = _request(app, "/dashboard/layout-engine-vue.es.js")
    assert status == 200
    header_map = dict(headers)
    assert header_map.get("content-type", "").startswith("application/javascript")
    assert b"createLayoutApp" in body

    status_core, _, _ = _request(app, "/dashboard/core/index.js")
    assert status_core == 200


def test_create_layout_app_helper_wraps_manifest_app():
    manifest = {"kind": "layout_manifest", "version": "from-helper"}

    helper_app = create_layout_app(
        manifest_builder=lambda: manifest,
        mount_path="/helper",
    )
    assert isinstance(helper_app, ManifestApp)

    app = helper_app.asgi_app()
    status, _, body = _request(app, "/helper/manifest.json")
    assert status == 200
    payload = json.loads(body.decode())
    assert payload["version"] == "from-helper"
