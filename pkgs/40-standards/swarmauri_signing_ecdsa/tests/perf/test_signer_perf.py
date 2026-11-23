import asyncio
from cryptography.hazmat.primitives.asymmetric import ec
import pytest

from swarmauri_signing_ecdsa import EcdsaEnvelopeSigner


@pytest.mark.perf
def test_sign_bytes_perf(benchmark):
    signer = EcdsaEnvelopeSigner()
    sk = ec.generate_private_key(ec.SECP256R1())
    key = {"kind": "cryptography_obj", "obj": sk}
    payload = b"perf-test"

    async def _sign():
        await signer.sign_bytes(key, payload)

    benchmark(lambda: asyncio.run(_sign()))
