import jwt
import pytest
from swarmauri_core.crypto.types import JWAAlg


@pytest.mark.unit
@pytest.mark.asyncio
async def test_jws_header_contains_alg_kid(service, provider) -> None:
    token = await service.mint({}, alg=JWAAlg.HS256)
    header = jwt.get_unverified_header(token)
    assert header["alg"] == JWAAlg.HS256.value
    assert header["kid"].startswith(provider.kid)
