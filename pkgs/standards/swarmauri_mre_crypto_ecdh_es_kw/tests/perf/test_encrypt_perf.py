import asyncio
from cryptography.hazmat.primitives.asymmetric import ec
import pytest

from swarmauri_mre_crypto_ecdh_es_kw import EcdhEsA128KwMreCrypto


@pytest.mark.perf
def test_encrypt_performance(benchmark) -> None:
    crypto = EcdhEsA128KwMreCrypto()
    sk = ec.generate_private_key(ec.SECP256R1())
    pk = sk.public_key()
    ref = {"kid": "1", "version": 1, "kind": "cryptography_obj", "obj": pk}

    async def run() -> None:
        await crypto.encrypt_for_many([ref], b"perf")

    benchmark(lambda: asyncio.run(run()))
