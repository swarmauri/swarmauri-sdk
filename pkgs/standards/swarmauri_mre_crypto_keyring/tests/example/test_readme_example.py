import secrets

import pytest

from swarmauri_mre_crypto_keyring import KeyringMreCrypto


class MemoryKeyring:
    """In-memory keyring used to demonstrate README usage."""

    def __init__(self) -> None:  # pragma: no cover - simple init
        self._store: dict[bytes, bytes] = {}

    def id(self) -> str:  # pragma: no cover - simple return
        return "memory"

    async def wrap_cek(self, cek: bytes, *, context):  # pragma: no cover
        token = secrets.token_bytes(8)
        self._store[token] = cek
        return token

    async def unwrap_cek(self, header: bytes, *, context):  # pragma: no cover
        return self._store[header]


@pytest.mark.asyncio
@pytest.mark.example
async def test_readme_usage_example() -> None:
    keyring = MemoryKeyring()
    keyref = {"kind": "keyring_client", "client": keyring}
    crypto = KeyringMreCrypto()

    env = await crypto.encrypt_for_many([keyref], b"hello")
    pt = await crypto.open_for(keyref, env)

    assert pt == b"hello"
