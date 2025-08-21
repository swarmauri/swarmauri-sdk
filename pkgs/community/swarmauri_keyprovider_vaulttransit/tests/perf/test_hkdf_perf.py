import asyncio
from types import SimpleNamespace

import pytest

from swarmauri_keyprovider_vaulttransit.VaultTransitKeyProvider import (
    VaultTransitKeyProvider,
)


class DummyProvider(VaultTransitKeyProvider):
    def __init__(self) -> None:  # pragma: no cover - used only in tests
        self._prefer_vault_rng = False
        self._client = SimpleNamespace(
            sys=SimpleNamespace(generate_random_bytes=lambda n_bytes: {})
        )


@pytest.mark.perf
def test_hkdf_performance(benchmark) -> None:
    provider = DummyProvider()

    def run() -> None:
        asyncio.run(provider.hkdf(b"ikm", salt=b"s", info=b"i", length=32))

    benchmark(run)
