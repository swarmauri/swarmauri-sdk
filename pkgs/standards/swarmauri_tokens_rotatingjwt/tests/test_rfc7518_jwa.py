import pytest
from swarmauri_core.crypto.types import JWAAlg


@pytest.mark.unit
@pytest.mark.asyncio
async def test_supports_requested_algorithm(service) -> None:
    info = service.supports()
    assert JWAAlg.HS256 in info["algs"]
