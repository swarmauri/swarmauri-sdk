import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from swarmauri_middleware_stdio import StdioMiddleware


@pytest.mark.i9n
def test_fastapi_integration() -> None:
    app = FastAPI()
    app.middleware("http")(StdioMiddleware().dispatch)

    @app.get("/ping")
    async def ping() -> dict[str, bool]:
        return {"pong": True}

    client = TestClient(app)
    response = client.get("/ping")
    assert response.json() == {"pong": True}
