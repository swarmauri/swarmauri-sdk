import jwt
import pytest


@pytest.mark.unit
@pytest.mark.asyncio
async def test_jws_header_contains_alg_kid(service, provider) -> None:
    token = await service.mint({}, alg="HS256")
    header = jwt.get_unverified_header(token)
    assert header["alg"] == "HS256"
    assert header["kid"].startswith(provider.kid)
