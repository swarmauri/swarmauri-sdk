from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.testclient import TestClient

from swarmauri_middleware_cachecontrol import CacheControlMiddleware

app = Starlette()
cache_control = CacheControlMiddleware(max_age=60)


async def apply_cache_control(request: Request, call_next):
    return await cache_control.dispatch(request, call_next)


app.add_middleware(BaseHTTPMiddleware, dispatch=apply_cache_control)


async def status(_request):
    return JSONResponse({"state": "fresh"})


app.add_route("/status", status)


def main() -> None:
    client = TestClient(app)
    response = client.get("/status")
    response.raise_for_status()

    print("Cache-Control:", response.headers["Cache-Control"])
    print("ETag:", response.headers["ETag"])
    print("Vary:", response.headers["Vary"])
    print("Payload:", response.json())


if __name__ == "__main__":
    main()
