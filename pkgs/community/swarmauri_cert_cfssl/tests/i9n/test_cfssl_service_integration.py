"""Integration tests for CfsslCertService using mocked HTTP calls."""

import pytest

from swarmauri_cert_cfssl import CfsslCertService
from swarmauri_core.crypto.types import KeyRef, KeyType, KeyUse, ExportPolicy


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_sign_cert(monkeypatch, csr_pem: bytes, cert_pem: bytes) -> None:
    """Sign a CSR and receive a certificate."""
    svc = CfsslCertService(base_url="https://cfssl.example")

    async def fake_post(path: str, payload):
        assert path == "/api/v1/cfssl/sign"
        return {"result": {"certificate": cert_pem.decode()}}

    monkeypatch.setattr(svc, "_post", fake_post)
    key = KeyRef(
        kid="k1",
        version=1,
        type=KeyType.RSA,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.PUBLIC_ONLY,
    )
    cert = await svc.sign_cert(csr_pem, key)
    assert b"BEGIN CERTIFICATE" in cert


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_verify_cert(monkeypatch, cert_pem: bytes) -> None:
    """Verify a certificate via CFSSL bundler."""
    svc = CfsslCertService(base_url="https://cfssl.example")

    async def fake_post(path: str, payload):
        assert path == "/api/v1/cfssl/bundle"
        return {"result": {"bundle": cert_pem.decode()}}

    monkeypatch.setattr(svc, "_post", fake_post)
    res = await svc.verify_cert(cert_pem, opts={"use_bundle": True})
    assert res["valid"] is True
    assert res["chain_len"] == 1
