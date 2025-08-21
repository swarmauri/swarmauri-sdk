"""CSR generation tests per RFC 2986."""

import asyncio

from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse
from swarmauri_standards.certs.AzureKeyVaultCertService import AzureKeyVaultCertService


def _make_keyref() -> KeyRef:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption(),
    )
    return KeyRef(
        kid="local",
        version="1",
        type=KeyType.RSA,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=pem,
        public=None,
        tags=None,
        uri=None,
    )


def test_create_csr_rfc2986() -> None:
    service = AzureKeyVaultCertService("https://example.vault.azure.net")
    keyref = _make_keyref()
    subject = {"CN": "example"}
    csr_pem = asyncio.run(service.create_csr(keyref, subject))
    csr = x509.load_pem_x509_csr(csr_pem)
    cn = csr.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
    assert cn == "example"
