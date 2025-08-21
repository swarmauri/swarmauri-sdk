import asyncio
import datetime as dt

import httpx
import pytest
import respx
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse
from swarmauri_certservice_stepca import StepCaCertService


@pytest.fixture
def rsa_keyref() -> KeyRef:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    return KeyRef(
        kid="test",
        version=1,
        type=KeyType.RSA,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=pem,
    )


@pytest.mark.i9n
@respx.mock
def test_sign_cert_rfc5280(rsa_keyref: KeyRef) -> None:
    service = StepCaCertService("https://ca.example")
    csr = asyncio.run(service.create_csr(rsa_keyref, {"CN": "example"}))

    ca_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "example")])
    now = dt.datetime.now(dt.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(ca_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + dt.timedelta(days=1))
        .sign(ca_key, hashes.SHA256())
    )
    cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode()

    respx.post("https://ca.example/1.0/sign").mock(
        return_value=httpx.Response(200, json={"crt": cert_pem})
    )

    async def run() -> bytes:
        return await service.sign_cert(csr, rsa_keyref, opts={"ott": "token"})

    cert_bytes = asyncio.run(run())
    parsed = x509.load_pem_x509_certificate(cert_bytes)
    assert (
        parsed.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value == "example"
    )
