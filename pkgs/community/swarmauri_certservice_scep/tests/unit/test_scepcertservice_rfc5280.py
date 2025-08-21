import pytest
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes, serialization
from datetime import datetime, timedelta

from swarmauri_certservice_scep import ScepCertService


@pytest.mark.unit
@pytest.mark.asyncio
async def test_verify_cert_rfc5280() -> None:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "example.com")])
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(subject)
        .public_key(key.public_key())
        .serial_number(1)
        .not_valid_before(datetime.utcnow())
        .not_valid_after(datetime.utcnow() + timedelta(days=1))
        .sign(key, hashes.SHA256())
    )
    cert_pem = cert.public_bytes(serialization.Encoding.PEM)
    svc = ScepCertService("https://scep.test")
    info = await svc.verify_cert(cert_pem)
    assert info["serial"] == 1
    assert info["subject"].endswith("CN=example.com")
