from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from swarmauri_middleware_llamaguard import LlamaGuardMiddleware

app = Starlette()
middleware = LlamaGuardMiddleware()  # Uses GROQ_API_KEY from the environment


async def llama_guard(request: Request, call_next):
    return await middleware.dispatch(request, call_next)


app.add_middleware(BaseHTTPMiddleware, dispatch=llama_guard)


async def health_check(_request):
    return JSONResponse({"status": "ok"})


app.add_route("/health", health_check)
