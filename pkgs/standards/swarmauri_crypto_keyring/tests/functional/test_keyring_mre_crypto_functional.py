import pytest
from swarmauri_crypto_keyring import KeyringMreCrypto


class DummyKeyring:
    def __init__(self, name):
        self._name = name

    def id(self) -> str:  # pragma: no cover - simple return
        return self._name

    async def wrap_cek(self, cek: bytes, *, context):  # pragma: no cover
        return cek

    async def unwrap_cek(self, header: bytes, *, context):  # pragma: no cover
        return header


@pytest.mark.asyncio
@pytest.mark.functional
async def test_encrypt_decrypt_roundtrip():
    crypto = KeyringMreCrypto()
    keyrings = [
        {"kind": "keyring_client", "client": DummyKeyring("a")},
        {"kind": "keyring_client", "client": DummyKeyring("b")},
    ]
    env = await crypto.encrypt_for_many(keyrings, b"secret", opts={"quorum_k": 2})
    pt = await crypto.open_for_many(keyrings, env)
    assert pt == b"secret"
