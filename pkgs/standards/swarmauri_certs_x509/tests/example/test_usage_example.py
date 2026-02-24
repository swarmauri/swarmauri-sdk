import asyncio
import pytest

from swarmauri_certs_x509 import X509CertService
from swarmauri_keyprovider_local import LocalKeyProvider
from swarmauri_core.key_providers.types import KeySpec, KeyAlg, KeyClass
from swarmauri_core.crypto.types import KeyUse, ExportPolicy


@pytest.mark.example
def test_readme_usage_example() -> None:
    svc = X509CertService()
    kp = LocalKeyProvider()
    spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.ED25519,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    )
    ca_key = asyncio.run(kp.create_key(spec))
    ca_cert = asyncio.run(svc.create_self_signed(ca_key, {"CN": "Example CA"}))

    leaf_key = asyncio.run(kp.create_key(spec))
    csr = asyncio.run(svc.create_csr(leaf_key, {"CN": "example.org"}))
    leaf_cert = asyncio.run(svc.sign_cert(csr, ca_key, ca_cert=ca_cert))

    result = asyncio.run(svc.verify_cert(leaf_cert, trust_roots=[ca_cert]))
    assert result["valid"] is True
