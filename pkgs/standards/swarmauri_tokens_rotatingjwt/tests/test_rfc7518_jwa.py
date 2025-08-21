import pytest


@pytest.mark.unit
@pytest.mark.asyncio
async def test_supports_requested_algorithm(service) -> None:
    info = service.supports()
    assert "HS256" in info["algs"]
