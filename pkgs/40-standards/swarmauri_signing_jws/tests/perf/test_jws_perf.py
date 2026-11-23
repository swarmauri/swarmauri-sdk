import asyncio
import pytest

from swarmauri_signing_jws import JwsSignerVerifier
from swarmauri_core.crypto.types import JWAAlg


@pytest.mark.perf
def test_sign_compact_perf(benchmark) -> None:
    jws = JwsSignerVerifier()
    key = {"kind": "raw", "key": "c" * 32}
    payload = {"msg": "perf"}

    async def _sign() -> None:
        await jws.sign_compact(payload=payload, alg=JWAAlg.HS256, key=key)

    benchmark(lambda: asyncio.run(_sign()))
