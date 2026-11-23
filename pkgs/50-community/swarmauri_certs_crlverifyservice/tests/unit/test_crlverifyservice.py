import pytest

from swarmauri_certs_crlverifyservice import CrlVerifyService


@pytest.mark.asyncio
async def test_verify_cert_valid(cert_and_crl) -> None:
    cert, crls = cert_and_crl()
    svc = CrlVerifyService()
    result = await svc.verify_cert(cert, crls=crls)
    assert result["valid"] is True
    assert result["revoked"] is False


@pytest.mark.asyncio
async def test_verify_cert_revoked(cert_and_crl) -> None:
    cert, crls = cert_and_crl(revoked=True)
    svc = CrlVerifyService()
    result = await svc.verify_cert(cert, crls=crls)
    assert result["valid"] is False
    assert result["revoked"] is True
    assert result["reason"] == "revoked"


@pytest.mark.asyncio
async def test_verify_cert_expired(cert_and_crl) -> None:
    cert, crls = cert_and_crl(expired=True)
    svc = CrlVerifyService()
    result = await svc.verify_cert(cert, crls=crls)
    assert result["valid"] is False
    assert result["reason"] == "expired_or_not_yet_valid"
