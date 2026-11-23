import asyncio
import gzip
from starlette.requests import Request
from starlette.responses import Response

from swarmauri_middleware_gzipcompression import GzipCompressionMiddleware

middleware = GzipCompressionMiddleware()


async def _handle_request() -> None:
    scope = {
        "type": "http",
        "method": "GET",
        "headers": [(b"accept-encoding", b"gzip")],
    }

    async def receive() -> dict:
        return {"type": "http.request", "body": b""}

    request = Request(scope, receive=receive)

    async def call_next(_: Request) -> Response:
        return Response(
            content='{"message":"Hello, gzip!"}',
            media_type="application/json",
        )

    response = await middleware.dispatch(request, call_next)

    assert response.headers.get("Content-Encoding") == "gzip"
    body = gzip.decompress(response.body).decode("utf-8")
    assert body == '{"message":"Hello, gzip!"}'


def run_example() -> None:
    asyncio.run(_handle_request())


if __name__ == "__main__":
    run_example()
