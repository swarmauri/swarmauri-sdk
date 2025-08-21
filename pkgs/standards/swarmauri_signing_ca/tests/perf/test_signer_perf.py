import asyncio
from cryptography.hazmat.primitives.asymmetric import ed25519
import pytest

from swarmauri_signing_ca import CASigner


@pytest.mark.perf
def test_sign_bytes_perf(benchmark):
    signer = CASigner()
    sk = ed25519.Ed25519PrivateKey.generate()
    key = {"kind": "cryptography_obj", "obj": sk}
    payload = b"perf-test"

    async def _sign():
        await signer.sign_bytes(key, payload)

    benchmark(lambda: asyncio.run(_sign()))
