import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from swarmauri_middleware_jsonrpc import JsonRpcMiddleware


@pytest.mark.i9n
def test_fastapi_integration() -> None:
    app = FastAPI()
    app.middleware("http")(JsonRpcMiddleware().dispatch)

    @app.post("/")
    async def endpoint(data: dict) -> dict:
        return {"ok": True}

    client = TestClient(app)
    resp = client.post("/", json={"jsonrpc": "2.0", "id": 1})
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}
