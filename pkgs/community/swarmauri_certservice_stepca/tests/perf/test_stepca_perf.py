import asyncio

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse
from swarmauri_certservice_stepca import StepCaCertService


def _keyref() -> KeyRef:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    return KeyRef(
        kid="perf",
        version=1,
        type=KeyType.RSA,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=pem,
    )


@pytest.mark.perf
def test_create_csr_perf(benchmark) -> None:
    service = StepCaCertService("https://ca.example")
    key = _keyref()

    def run() -> None:
        asyncio.run(service.create_csr(key, {"CN": "perf"}))

    benchmark(run)
