import asyncio
from cryptography.hazmat.primitives.asymmetric import rsa
import pytest

from swarmauri_signing_rsa import RSAEnvelopeSigner


@pytest.mark.perf
def test_sign_bytes_perf(benchmark):
    signer = RSAEnvelopeSigner()
    sk = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    key = {"kind": "cryptography_obj", "obj": sk}
    payload = b"perf-test"

    async def _sign():
        await signer.sign_bytes(key, payload)

    benchmark(lambda: asyncio.run(_sign()))
