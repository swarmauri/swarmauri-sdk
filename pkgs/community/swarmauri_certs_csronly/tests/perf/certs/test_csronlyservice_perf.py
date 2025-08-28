import asyncio
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from swarmauri_certs_csronly import CsrOnlyService
from swarmauri_core.certs.ICertService import SubjectSpec
from swarmauri_core.crypto.types import KeyRef, KeyType, KeyUse, ExportPolicy


@pytest.mark.perf
def test_create_csr_perf(benchmark) -> None:
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
    subject: SubjectSpec = {"CN": "perf"}

    def run() -> bytes:
        return asyncio.run(svc.create_csr(key_ref, subject))

    result = benchmark(run)
    assert b"BEGIN CERTIFICATE REQUEST" in result
