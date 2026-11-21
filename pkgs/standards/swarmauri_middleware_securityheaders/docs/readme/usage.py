from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from swarmauri_middleware_securityheaders import SecurityHeadersMiddleware

app = Starlette()
security_middleware = SecurityHeadersMiddleware(app)


async def apply_security_headers(request: Request, call_next):
    return await security_middleware.dispatch(request, call_next)


app.add_middleware(BaseHTTPMiddleware, dispatch=apply_security_headers)


async def read_root(_request):
    return JSONResponse({"status": "ok"})


app.add_route("/", read_root)
