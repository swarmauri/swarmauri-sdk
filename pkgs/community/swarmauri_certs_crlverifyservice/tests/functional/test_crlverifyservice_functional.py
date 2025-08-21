import pytest

from swarmauri_certs_crlverifyservice import CrlVerifyService


@pytest.mark.asyncio
async def test_verify_and_parse(cert_and_crl) -> None:
    cert, crls = cert_and_crl()
    svc = CrlVerifyService()
    verify = await svc.verify_cert(cert, crls=crls)
    assert verify["valid"] is True
    parsed = await svc.parse_cert(cert)
    assert parsed["subject"] == "CN=EE"
