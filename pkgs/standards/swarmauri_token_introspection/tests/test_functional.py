import pytest
import httpx

from swarmauri_token_introspection import IntrospectionTokenService


@pytest.mark.acceptance
@pytest.mark.asyncio
async def test_jwks_fetch(monkeypatch):
    jwks_payload = {"keys": ["k"]}

    async def handler(request):
        if request.url.path == "/jwks":
            return httpx.Response(200, json=jwks_payload)
        return httpx.Response(200, json={"active": True})

    transport = httpx.MockTransport(handler)
    service = IntrospectionTokenService(
        "https://example.com/introspect",
        client_id="c",
        client_secret="s",
        jwks_url="https://example.com/jwks",
    )
    service._client = httpx.AsyncClient(transport=transport)
    await service.verify("tok")
    jwks = await service.jwks()
    assert jwks == jwks_payload
