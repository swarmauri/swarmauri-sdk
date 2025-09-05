import pytest
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.x509.oid import NameOID

from swarmauri_certs_csronly import CsrOnlyService
from swarmauri_core.certs.ICertService import SubjectSpec
from swarmauri_core.crypto.types import KeyRef, KeyType, KeyUse, ExportPolicy


@pytest.mark.acceptance
@pytest.mark.asyncio
async def test_create_csr_generates_valid_pem() -> None:
    svc = CsrOnlyService()
    key = ed25519.Ed25519PrivateKey.generate()
    pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    key_ref = KeyRef(
        kid="k1",
        version=1,
        type=KeyType.ED25519,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=pem,
    )
    subject: SubjectSpec = {"CN": "example.com"}
    csr = await svc.create_csr(key_ref, subject)
    assert b"BEGIN CERTIFICATE REQUEST" in csr
    loaded = x509.load_pem_x509_csr(csr)
    cn = loaded.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
    assert cn == "example.com"
