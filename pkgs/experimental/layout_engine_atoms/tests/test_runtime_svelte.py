from fastapi import FastAPI, Request
from starlette.testclient import TestClient

from layout_engine_atoms.runtime.svelte import mount_svelte_app, SvelteLayoutOptions
from layout_engine_atoms.runtime.vue.realtime import RealtimeChannel, RealtimeOptions


def _manifest_payload():
    return {
        "kind": "LayoutManifest",
        "version": "test",
        "viewport": {"width": 800, "height": 600},
        "grid": {},
        "tiles": [
            {
                "id": "hero",
                "role": "swarmakit:svelte:cardbased-list",
                "frame": {"x": 0, "y": 0, "w": 400, "h": 300},
                "props": {},
                "atom": {
                    "role": "swarmakit:svelte:cardbased-list",
                    "module": "@swarmakit/svelte",
                    "export": "CardbasedList",
                    "version": "0.0.22",
                },
            }
        ],
    }


def test_mount_svelte_app_serves_manifest_with_realtime_metadata():
    app = FastAPI()

    async def builder(_: Request):
        return _manifest_payload()

    mount_svelte_app(
        app,
        builder,
        base_path="/",
        realtime=RealtimeOptions(
            path="/ws/demo",
            channels=(RealtimeChannel(id="demo.channel"),),
        ),
        layout_options=SvelteLayoutOptions(),
    )

    client = TestClient(app)
    manifest = client.get("/manifest.json").json()

    assert manifest["channels"][0]["id"] == "demo.channel"
    assert manifest["ws_routes"][0]["path"].endswith("/ws/demo")


def test_mount_svelte_app_serves_shell_html():
    app = FastAPI()

    async def builder(_: Request):
        return _manifest_payload()

    mount_svelte_app(app, builder, base_path="/", layout_options=SvelteLayoutOptions())
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "layout-engine-svelte" in response.text
