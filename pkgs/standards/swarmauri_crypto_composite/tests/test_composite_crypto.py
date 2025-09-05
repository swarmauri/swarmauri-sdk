import pytest

from swarmauri_crypto_composite import CompositeCrypto
from swarmauri_core.crypto.ICrypto import ICrypto
from swarmauri_core.crypto.types import (
    AEADCiphertext,
    KeyRef,
    KeyType,
    KeyUse,
    ExportPolicy,
)


class DummyCrypto(ICrypto):
    def __init__(self, name: str, alg: str):
        self.name = name
        self._alg = alg

    def supports(self):
        return {"encrypt": (self._alg,)}

    async def encrypt(self, key, pt, *, alg=None, aad=None, nonce=None):
        return AEADCiphertext(
            kid="k",
            version=1,
            alg=alg or self._alg,
            nonce=b"",
            ct=self.name.encode(),
            tag=b"",
        )

    async def decrypt(self, key, ct, *, aad=None):  # pragma: no cover - unused
        raise NotImplementedError

    async def wrap(
        self, kek, *, dek=None, wrap_alg=None, nonce=None
    ):  # pragma: no cover - unused
        raise NotImplementedError

    async def unwrap(self, kek, wrapped):  # pragma: no cover - unused
        raise NotImplementedError

    async def encrypt_for_many(
        self,
        recipients,
        pt,
        *,
        enc_alg=None,
        recipient_wrap_alg=None,
        aad=None,
        nonce=None,
    ):  # pragma: no cover - unused
        raise NotImplementedError

    async def seal(self, recipient, pt, *, alg=None):  # pragma: no cover - unused
        raise NotImplementedError

    async def unseal(
        self, recipient_priv, sealed, *, alg=None
    ):  # pragma: no cover - unused
        raise NotImplementedError


@pytest.mark.asyncio
async def test_encrypt_routing():
    p1 = DummyCrypto("one", "alg1")
    p2 = DummyCrypto("two", "alg2")
    comp = CompositeCrypto([p1, p2])
    key = KeyRef(
        kid="k",
        version=1,
        type=KeyType.SYMMETRIC,
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=b"\x00" * 32,
    )

    ct = await comp.encrypt(key, b"data", alg="alg2")
    assert ct.ct == b"two"
