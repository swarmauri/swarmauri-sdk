from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from swarmauri_middleware_circuitbreaker import CircuitBreakerMiddleware

app = Starlette()
breaker = CircuitBreakerMiddleware(
    fail_max=5,
    reset_timeout=30,
    half_open_wait_time=10,
)


async def check_circuit(request, call_next):
    try:
        return await breaker.dispatch(request, call_next)
    except HTTPException as exc:
        return JSONResponse(
            {"detail": exc.detail},
            status_code=exc.status_code,
            headers=exc.headers,
        )


app.add_middleware(BaseHTTPMiddleware, dispatch=check_circuit)
