import asyncio

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import serialization
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


@pytest.mark.unit
def test_docstring_mentions_rfc2986() -> None:
    assert "RFC 2986" in StepCaCertService.__doc__


@pytest.mark.unit
def test_create_csr_rfc2986(rsa_keyref: KeyRef) -> None:
    service = StepCaCertService("https://ca.example")
    csr_bytes = asyncio.run(service.create_csr(rsa_keyref, {"CN": "example"}))
    csr = x509.load_pem_x509_csr(csr_bytes)
    assert csr.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value == "example"
