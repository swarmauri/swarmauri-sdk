import asyncio
from types import SimpleNamespace
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import pytest

from swarmauri_signing_ca import CASigner


@pytest.mark.perf
def test_sign_bytes_perf(benchmark):
    signer = CASigner()
    sk = Ed25519PrivateKey.generate()
    key = SimpleNamespace(tags={"crypto_obj": sk})
    payload = b"perf-test"

    async def _sign():
        await signer.sign_bytes(key, payload)

    benchmark(lambda: asyncio.run(_sign()))
