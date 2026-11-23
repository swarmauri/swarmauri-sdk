import pytest
import httpx

from swarmauri_tokens_introspection import IntrospectionTokenService


@pytest.mark.test
@pytest.mark.asyncio
async def test_missing_active_field():
    async def handler(request):
        return httpx.Response(200, json={})

    transport = httpx.MockTransport(handler)
    service = IntrospectionTokenService(
        "https://example.com/introspect",
        client_id="c",
        client_secret="s",
    )
    service._client = httpx.AsyncClient(transport=transport)
    with pytest.raises(ValueError):
        await service.verify("tok")
