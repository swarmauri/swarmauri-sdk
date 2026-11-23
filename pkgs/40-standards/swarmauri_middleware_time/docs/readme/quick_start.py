from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.testclient import TestClient

from swarmauri_middleware_time import TimerMiddleware

app = Starlette()
timer_middleware = TimerMiddleware()


async def add_timer(request: Request, call_next):
    return await timer_middleware.dispatch(request, call_next)


app.add_middleware(BaseHTTPMiddleware, dispatch=add_timer)


async def ping(_request):
    return JSONResponse({"message": "pong"})


app.add_route("/ping", ping)

if __name__ == "__main__":
    client = TestClient(app)
    response = client.get("/ping")

    assert response.json() == {"message": "pong"}
    assert "X-Request-Duration" in response.headers
    assert float(response.headers["X-Request-Duration"]) >= 0.0
    assert "X-Request-Start-Time" in response.headers

    print("Duration header:", response.headers["X-Request-Duration"])
    print("Start time header:", response.headers["X-Request-Start-Time"])
