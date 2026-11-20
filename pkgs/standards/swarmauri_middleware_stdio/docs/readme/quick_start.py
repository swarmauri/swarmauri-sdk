import logging
import sys

from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from swarmauri_middleware_stdio import StdioMiddleware

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

app = Starlette()
stdio = StdioMiddleware()


async def log_to_stdout(request: Request, call_next):
    return await stdio.dispatch(request, call_next)


app.add_middleware(BaseHTTPMiddleware, dispatch=log_to_stdout)


async def hello(_request):
    return JSONResponse({"message": "hello"})


app.add_route("/", hello)
