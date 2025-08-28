import asyncio
import pytest
from cryptography.hazmat.primitives.asymmetric import ec

from swarmauri_signing_secp256k1 import Secp256k1EnvelopeSigner


@pytest.mark.perf
def test_sign_bytes_perf(benchmark):
    signer = Secp256k1EnvelopeSigner()
    sk = ec.generate_private_key(ec.SECP256K1())
    key = {"kind": "cryptography_obj", "obj": sk}
    payload = b"perf-test"

    async def _sign():
        await signer.sign_bytes(key, payload)

    benchmark(lambda: asyncio.run(_sign()))
