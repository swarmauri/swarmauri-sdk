import asyncio
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
import pytest

from swarmauri_mre_crypto_age import AgeMreCrypto


@pytest.mark.perf
def test_encrypt_performance(benchmark) -> None:
    crypto = AgeMreCrypto()
    sk = X25519PrivateKey.generate()
    pk = sk.public_key()
    ref = {"kind": "cryptography_obj", "obj": pk}

    async def run() -> None:
        await crypto.encrypt_for_many([ref], b"perf")

    benchmark(lambda: asyncio.run(run()))
