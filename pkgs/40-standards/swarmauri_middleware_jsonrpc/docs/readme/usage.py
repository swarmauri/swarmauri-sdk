from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from swarmauri_middleware_jsonrpc import JsonRpcMiddleware

app = Starlette()
app.add_middleware(BaseHTTPMiddleware, dispatch=JsonRpcMiddleware().dispatch)
