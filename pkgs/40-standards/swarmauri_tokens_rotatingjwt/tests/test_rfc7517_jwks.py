import pytest
from swarmauri_core.crypto.types import JWAAlg


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_jwks_retains_previous_versions(rotating_service) -> None:
    await rotating_service.mint({}, alg=JWAAlg.HS256)
    await rotating_service.mint({}, alg=JWAAlg.HS256)
    keys = await rotating_service.jwks()
    kids = {k["kid"] for k in keys["keys"]}
    assert any(kid.endswith(".1") for kid in kids)
    assert any(kid.endswith(".2") for kid in kids)
