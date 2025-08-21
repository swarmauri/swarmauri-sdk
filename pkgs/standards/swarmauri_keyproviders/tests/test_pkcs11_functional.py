import asyncio

import pytest

from swarmauri_keyproviders import Pkcs11KeyProvider


@pytest.mark.func
@pytest.mark.asyncio
async def test_hkdf_derivation() -> None:
    """Deriving bytes via HKDF should yield requested length."""
    provider = object.__new__(Pkcs11KeyProvider)
    result = await Pkcs11KeyProvider.hkdf(
        provider, b"input", salt=b"salt", info=b"info", length=32
    )
    assert len(result) == 32


@pytest.mark.perf
def test_hkdf_performance(benchmark) -> None:
    """Benchmark HKDF derivation for basic performance check."""
    provider = object.__new__(Pkcs11KeyProvider)

    async def run() -> None:
        await Pkcs11KeyProvider.hkdf(
            provider, b"input", salt=b"salt", info=b"info", length=32
        )

    benchmark(lambda: asyncio.run(run()))
