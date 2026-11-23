from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.testclient import TestClient
from swarmauri_middleware_ratelimit import RateLimitMiddleware

app = Starlette()
rate_limiter = RateLimitMiddleware(rate_limit=2, time_window=60)


async def limit_requests(request, call_next):
    return await rate_limiter.dispatch(request, call_next)


app.add_middleware(BaseHTTPMiddleware, dispatch=limit_requests)


async def ping(_request):
    return JSONResponse({"status": "ok"})


app.add_route("/ping", ping)

client = TestClient(app)

assert client.get("/ping").status_code == 200
assert client.get("/ping").status_code == 200
assert client.get("/ping").status_code == 429
