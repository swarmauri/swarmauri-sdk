import pytest


@pytest.mark.asyncio
async def test_sign_and_verify_certificate(composite, sample_key):
    cert = await composite.sign_cert(b"csr-bytes", sample_key)
    assert cert == b"cert-B"
    info = await composite.verify_cert(cert)
    assert info["backend"] == "A"
    parsed = await composite.parse_cert(cert)
    assert parsed["backend"] == "A"
