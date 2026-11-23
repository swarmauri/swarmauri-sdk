import asyncio
import pytest
from swarmauri_mre_crypto_keyring import KeyringMreCrypto


class DummyKeyring:
    def __init__(self, name):
        self._name = name

    def id(self) -> str:  # pragma: no cover
        return self._name

    async def wrap_cek(self, cek: bytes, *, context):  # pragma: no cover
        return cek

    async def unwrap_cek(self, header: bytes, *, context):  # pragma: no cover
        return header


@pytest.mark.perf
def test_encrypt_perf(benchmark):
    crypto = KeyringMreCrypto()
    keyrings = [
        {"kind": "keyring_client", "client": DummyKeyring("a")}
    ]  # one recipient

    async def run():
        await crypto.encrypt_for_many(keyrings, b"data")

    benchmark(lambda: asyncio.run(run()))
