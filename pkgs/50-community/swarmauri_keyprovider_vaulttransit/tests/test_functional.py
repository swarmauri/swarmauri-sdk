import pytest


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_get_public_jwk(provider):
    jwk = await provider.get_public_jwk("test", 1)
    assert jwk["kty"] == "RSA"
