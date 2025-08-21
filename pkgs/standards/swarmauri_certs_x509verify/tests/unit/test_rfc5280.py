import asyncio
import datetime

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.x509.oid import NameOID

from swarmauri_certs_x509verify import X509VerifyService


def _future_self_signed() -> bytes:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "future.test")])
    builder = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow() + datetime.timedelta(days=1))
        .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=2))
    )
    cert = builder.sign(key, hashes.SHA256())
    return cert.public_bytes(Encoding.PEM)


@pytest.mark.unit
def test_rfc5280_not_yet_valid() -> None:
    """Validate notBefore handling (RFC 5280 §4.1.2.5)."""
    cert = _future_self_signed()
    svc = X509VerifyService()
    result = asyncio.run(svc.verify_cert(cert, trust_roots=[cert]))
    assert not result["valid"]
    assert result["reason"] == "invalid_chain_or_time"
