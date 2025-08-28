import datetime as dt

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.x509.oid import NameOID

pytest.importorskip("pkcs11")

from swarmauri_certs_pkcs11 import Pkcs11CertService


@pytest.mark.asyncio
@pytest.mark.test
@pytest.mark.functional
async def test_verify_self_signed_cert() -> None:
    key = ed25519.Ed25519PrivateKey.generate()
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "example")])
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=1))
        .not_valid_after(dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=1))
        .sign(key, None)
    )
    cert_pem = cert.public_bytes(serialization.Encoding.PEM)
    svc = Pkcs11CertService(module_path="/usr/lib/softhsm/libsofthsm2.so")
    result = await svc.verify_cert(cert_pem, trust_roots=[cert_pem])
    assert result["valid"]
    parsed = await svc.parse_cert(cert_pem)
    assert parsed["subject"]
