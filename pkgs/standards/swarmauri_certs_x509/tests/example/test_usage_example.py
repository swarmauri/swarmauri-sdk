import asyncio
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from swarmauri_certs_x509 import X509CertService
from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse


def _make_key_ref() -> KeyRef:
    sk = ed25519.Ed25519PrivateKey.generate()
    pem = sk.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    return KeyRef(
        kid="k1",
        version=1,
        type=KeyType.ED25519,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=pem,
        public=None,
        tags={},
    )


@pytest.mark.example
def test_readme_usage_example() -> None:
    svc = X509CertService()
    ca_key = _make_key_ref()
    ca_cert = asyncio.run(svc.create_self_signed(ca_key, {"CN": "Example CA"}))

    leaf_key = _make_key_ref()
    csr = asyncio.run(svc.create_csr(leaf_key, {"CN": "example.org"}))
    leaf_cert = asyncio.run(svc.sign_cert(csr, ca_key, ca_cert=ca_cert))

    result = asyncio.run(svc.verify_cert(leaf_cert, trust_roots=[ca_cert]))
    assert result["valid"] is True
