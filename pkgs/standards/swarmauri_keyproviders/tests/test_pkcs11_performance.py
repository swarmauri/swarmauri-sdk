"""Performance benchmark for HKDF per RFC 5869."""

import asyncio
import pytest

from swarmauri_keyproviders.Pkcs11KeyProvider import Pkcs11KeyProvider


@pytest.mark.perf
def test_hkdf_performance(benchmark) -> None:
    provider = Pkcs11KeyProvider.__new__(Pkcs11KeyProvider)

    def run() -> bytes:
        return asyncio.run(provider.hkdf(b"ikm", salt=b"salt", info=b"info", length=32))

    benchmark(run)
