import pytest


@pytest.mark.asyncio
async def test_backend_override(composite, sample_key):
    cert = await composite.create_self_signed(
        sample_key, {"CN": "example"}, opts={"backend": "B"}
    )
    assert cert == b"self-B"


@pytest.mark.asyncio
async def test_invalid_backend(composite, sample_key):
    with pytest.raises(ValueError):
        await composite.create_csr(
            sample_key, {"CN": "example"}, opts={"backend": "missing"}
        )
