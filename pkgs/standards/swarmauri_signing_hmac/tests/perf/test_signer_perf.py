import asyncio
import pytest

from swarmauri_core.crypto.types import JWAAlg
from swarmauri_signing_hmac import HmacEnvelopeSigner


@pytest.mark.perf
def test_sign_bytes_perf(benchmark):
    signer = HmacEnvelopeSigner()
    key = {"kind": "raw", "key": "secret"}
    payload = b"perf-test"

    async def _sign():
        await signer.sign_bytes(key, payload, alg=JWAAlg.HS256)

    benchmark(lambda: asyncio.run(_sign()))
