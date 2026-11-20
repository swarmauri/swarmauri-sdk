from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.testclient import TestClient

from swarmauri_middleware_logging import LoggingMiddleware

app = Starlette()
logging_middleware = LoggingMiddleware()


async def log_requests(request: Request, call_next):
    return await logging_middleware.dispatch(request, call_next)


app.add_middleware(BaseHTTPMiddleware, dispatch=log_requests)


async def echo(request: Request):
    return JSONResponse(await request.json())


app.add_route("/echo", echo, methods=["POST"])

client = TestClient(app)
print(client.post("/echo", json={"message": "hello"}).json())
