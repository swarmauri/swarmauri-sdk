import asyncio
import pytest

from swarmauri_signing_jws import JwsSignerVerifier


@pytest.mark.perf
def test_sign_compact_perf(benchmark) -> None:
    jws = JwsSignerVerifier()
    key = {"kind": "raw", "key": "secret"}
    payload = {"msg": "perf"}

    async def _sign() -> None:
        await jws.sign_compact(payload=payload, alg="HS256", key=key)

    benchmark(lambda: asyncio.run(_sign()))
