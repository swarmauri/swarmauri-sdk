import asyncio
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import pytest

from swarmauri_signing_ed25519 import Ed25519EnvelopeSigner


@pytest.mark.perf
def test_sign_bytes_perf(benchmark):
    signer = Ed25519EnvelopeSigner()
    sk = Ed25519PrivateKey.generate()
    key = {"kind": "cryptography_obj", "obj": sk}
    payload = b"perf-test"

    async def _sign():
        await signer.sign_bytes(key, payload)

    benchmark(lambda: asyncio.run(_sign()))
