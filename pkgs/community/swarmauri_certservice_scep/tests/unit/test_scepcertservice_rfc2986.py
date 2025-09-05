import pytest
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

from swarmauri_certservice_scep import ScepCertService
from swarmauri_core.crypto.types import KeyRef, KeyType, KeyUse, ExportPolicy


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_csr_rfc2986() -> None:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    key_ref = KeyRef(
        kid="k1",
        version=1,
        type=KeyType.RSA,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=pem,
    )
    svc = ScepCertService("https://scep.test", challenge_password="pass")
    csr_bytes = await svc.create_csr(
        key_ref, {"CN": "example.com"}, san={"dns": ["example.com"]}
    )
    csr = x509.load_pem_x509_csr(csr_bytes)
    cn = csr.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
    assert cn == "example.com"
    attr = csr.get_attribute_for_oid(x509.oid.AttributeOID.CHALLENGE_PASSWORD)
    assert attr == b"pass"
