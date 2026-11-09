import pytest
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.testclient import TestClient
from swarmauri_middleware_stdio import StdioMiddleware


@pytest.mark.i9n
def test_starlette_integration() -> None:
    app = Starlette()
    app.add_middleware(BaseHTTPMiddleware, dispatch=StdioMiddleware().dispatch)

    async def ping(_request):
        return JSONResponse({"pong": True})

    app.add_route("/ping", ping)
    client = TestClient(app)
    response = client.get("/ping")
    assert response.json() == {"pong": True}
