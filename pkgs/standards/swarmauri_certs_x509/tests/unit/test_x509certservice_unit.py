import asyncio

from swarmauri_certs_x509 import X509CertService


async def _mint_self_signed(make_key_ref) -> bytes:
    svc = X509CertService()
    key = make_key_ref()
    cert = await svc.create_self_signed(key, {"CN": "unit"})
    return cert


def test_create_self_signed_unit(make_key_ref) -> None:
    cert = asyncio.run(_mint_self_signed(make_key_ref))
    assert b"BEGIN CERTIFICATE" in cert
