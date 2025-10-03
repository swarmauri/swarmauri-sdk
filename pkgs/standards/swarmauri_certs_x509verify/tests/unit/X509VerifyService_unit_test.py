import asyncio
import datetime

import pytest
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.x509 import Name, NameAttribute
from cryptography.x509.oid import NameOID

from swarmauri_certs_x509verify import X509VerifyService
from cryptography import x509


def _create_self_signed() -> bytes:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = Name([NameAttribute(NameOID.COMMON_NAME, "unit.test")])
    builder = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow() - datetime.timedelta(days=1))
        .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=1))
    )
    cert = builder.sign(key, hashes.SHA256())
    return cert.public_bytes(Encoding.PEM)


@pytest.mark.unit
def test_parse_cert_unit() -> None:
    cert_bytes = _create_self_signed()
    svc = X509VerifyService()
    info = asyncio.run(svc.parse_cert(cert_bytes))
    assert info["subject"] == "CN=unit.test"
    assert info["issuer"] == "CN=unit.test"
