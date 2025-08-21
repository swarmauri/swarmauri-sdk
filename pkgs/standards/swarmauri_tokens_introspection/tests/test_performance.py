import asyncio

import httpx
import pytest

from swarmauri_tokens_introspection import IntrospectionTokenService


@pytest.mark.perf
def test_verify_performance(benchmark):
    async def handler(request):
        return httpx.Response(200, json={"active": True})

    transport = httpx.MockTransport(handler)
    service = IntrospectionTokenService(
        "https://example.com/introspect",
        client_id="c",
        client_secret="s",
    )
    service._client = httpx.AsyncClient(transport=transport)

    async def run():
        await service.verify("tok")

    benchmark(lambda: asyncio.run(run()))
