import pytest


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_jwks_retains_previous_versions(rotating_service) -> None:
    await rotating_service.mint({}, alg="HS256")
    await rotating_service.mint({}, alg="HS256")
    keys = await rotating_service.jwks()
    kids = {k["kid"] for k in keys["keys"]}
    assert any(kid.endswith(".1") for kid in kids)
    assert any(kid.endswith(".2") for kid in kids)
