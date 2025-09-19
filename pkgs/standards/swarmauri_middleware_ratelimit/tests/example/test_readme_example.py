"""Executable version of the README usage example."""

from collections.abc import Awaitable, Callable

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from starlette.responses import Response

from swarmauri_middleware_ratelimit import RateLimitMiddleware


@pytest.mark.example
def test_readme_rate_limit_example() -> None:
    """Verify the README example matches the actual middleware behavior."""

    app = FastAPI()
    rate_limiter = RateLimitMiddleware(rate_limit=2, time_window=60)

    @app.middleware("http")
    async def limit_requests(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        return await rate_limiter.dispatch(request, call_next)

    @app.get("/ping")
    async def ping() -> dict[str, str]:
        return {"status": "ok"}

    client = TestClient(app)

    assert client.get("/ping").status_code == 200
    assert client.get("/ping").status_code == 200

    response = client.get("/ping")
    assert response.status_code == 429
    assert response.text == "Rate limit exceeded"
