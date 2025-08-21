import pytest


@pytest.mark.asyncio
async def test_create_csr_routes_to_provider(composite, sample_key):
    csr = await composite.create_csr(sample_key, {"CN": "example"})
    assert csr == b"csr-A"
