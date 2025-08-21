import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

from swarmauri_certservice_ms_adcs import MsAdcsCertService, _AuthCfg
from swarmauri_core.crypto.types import KeyRef, KeyType, KeyUse, ExportPolicy
from swarmauri_core.certs.ICertService import SubjectSpec


@pytest.mark.asyncio
async def test_create_csr_pem_rfc2986() -> None:
    priv = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = priv.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    key = KeyRef(
        kid="k1",
        version=1,
        type=KeyType.RSA,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.PUBLIC_ONLY,
        material=pem,
    )
    svc = MsAdcsCertService(base_url="https://example.com", auth=_AuthCfg(mode="none"))
    subject: SubjectSpec = {"CN": "test"}
    csr = await svc.create_csr(key, subject)
    assert csr.startswith(b"-----BEGIN CERTIFICATE REQUEST-----")
