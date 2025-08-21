import pytest
import httpx

from swarmauri_token_introspection import IntrospectionTokenService


@pytest.mark.test
@pytest.mark.unit
@pytest.mark.asyncio
async def test_verify_active_token(monkeypatch):
    async def handler(request):
        assert request.method == "POST"
        return httpx.Response(200, json={"active": True, "sub": "abc"})

    transport = httpx.MockTransport(handler)
    service = IntrospectionTokenService(
        "https://example.com/introspect",
        client_id="c",
        client_secret="s",
    )
    service._client = httpx.AsyncClient(transport=transport)
    claims = await service.verify("tok")
    assert claims["sub"] == "abc"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_verify_inactive_token(monkeypatch):
    async def handler(request):
        return httpx.Response(200, json={"active": False})

    transport = httpx.MockTransport(handler)
    service = IntrospectionTokenService(
        "https://example.com/introspect",
        client_id="c",
        client_secret="s",
        negative_ttl_s=1,
    )
    service._client = httpx.AsyncClient(transport=transport)
    with pytest.raises(ValueError):
        await service.verify("tok")
    # Cached negative
    with pytest.raises(ValueError):
        await service.verify("tok")
