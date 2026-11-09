import pytest
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.testclient import TestClient
from swarmauri_middleware_jsonrpc import JsonRpcMiddleware


@pytest.mark.i9n
def test_starlette_integration() -> None:
    app = Starlette()
    app.add_middleware(
        BaseHTTPMiddleware, dispatch=JsonRpcMiddleware().dispatch
    )

    async def endpoint(data: dict):
        return JSONResponse({"ok": True})

    app.add_route("/", endpoint, methods=["POST"])
    client = TestClient(app)
    resp = client.post("/", json={"jsonrpc": "2.0", "id": 1})
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}
