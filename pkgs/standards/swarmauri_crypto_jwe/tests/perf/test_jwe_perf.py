import asyncio

import pytest

from swarmauri_crypto_jwe import JweCrypto


@pytest.mark.perf
@pytest.mark.test
def test_encrypt_perf(benchmark) -> None:  # type: ignore[no-untyped-def]
    crypto = JweCrypto()
    key = {"k": b"0" * 32}
    payload = b"a" * 1024

    async def _run() -> str:
        return await crypto.encrypt_compact(
            payload=payload, alg="dir", enc="A256GCM", key=key
        )

    benchmark(lambda: asyncio.run(_run()))
