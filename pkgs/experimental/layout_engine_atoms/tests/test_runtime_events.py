from fastapi import FastAPI, Request
from starlette.testclient import TestClient

from layout_engine_atoms.runtime.vue import UiEvent, UiEventResult, mount_layout_app


def _manifest_payload():
    return {
        "kind": "LayoutManifest",
        "version": "test",
        "viewport": {"width": 800, "height": 600},
        "grid": {},
        "tiles": [
            {
                "id": "metric",
                "role": "swarmakit:vue:progress-bar",
                "frame": {"x": 0, "y": 0, "w": 100, "h": 100},
                "props": {},
                "atom": {
                    "role": "swarmakit:vue:progress-bar",
                    "module": "@swarmakit/vue",
                    "export": "ProgressBar",
                    "version": "0.0.22",
                },
            }
        ],
    }


class DummyHub:
    def __init__(self) -> None:
        self.messages: list[tuple[str, dict]] = []

    async def broadcast(self, channel: str, payload: dict) -> None:
        self.messages.append((channel, dict(payload)))


def test_ui_event_invokes_handler_and_broadcasts_payload():
    app = FastAPI()
    call_log: list[dict] = []

    async def builder(_: Request):
        return _manifest_payload()

    async def handler(_: Request, payload: dict | None = None):
        payload = payload or {}
        call_log.append(payload)
        value = payload.get("value", 1)
        return UiEventResult(
            body={"received": value},
            channel="demo.channel",
            payload={"value": value},
        )

    mount_layout_app(
        app,
        manifest_builder=builder,
        base_path="/",
        events=(UiEvent(id="demo.event", handler=handler),),
    )

    app.state.layout_engine_realtime = DummyHub()

    client = TestClient(app)
    response = client.post("/events/demo.event", json={"value": 5})

    assert response.status_code == 200
    assert response.json()["payload"]["value"] == 5
    assert call_log == [{"value": 5}]
    assert app.state.layout_engine_realtime.messages == [
        ("demo.channel", {"value": 5})
    ]


def test_event_route_supports_get_queries():
    app = FastAPI()
    captured: list[dict] = []

    async def builder(_: Request):
        return _manifest_payload()

    async def handler(_: Request, payload: dict | None = None):
        captured.append(payload or {})
        return UiEventResult(body={"status": "ok"})

    mount_layout_app(
        app,
        manifest_builder=builder,
        base_path="/",
        events=(UiEvent(id="demo.query", handler=handler, method="GET"),),
    )

    client = TestClient(app)
    response = client.get("/events/demo.query?delta=3")

    assert response.status_code == 200
    assert captured == [{"delta": "3"}]
