"""Route crypto operations to the provider that supports the requested algorithm."""

import asyncio

from swarmauri_crypto_composite import CompositeCrypto
from swarmauri_core.crypto.ICrypto import ICrypto
from swarmauri_core.crypto.types import (
    AEADCiphertext,
    ExportPolicy,
    KeyRef,
    KeyType,
    KeyUse,
)


class DummyCrypto(ICrypto):
    def __init__(self, name: str, alg: str) -> None:
        self._name = name
        self._alg = alg

    def supports(self):
        return {"encrypt": (self._alg,)}

    async def encrypt(self, key, pt, *, alg=None, aad=None, nonce=None):
        return AEADCiphertext(
            kid="dummy",
            version=1,
            alg=alg or self._alg,
            nonce=b"",
            ct=self._name.encode(),
            tag=b"",
        )

    async def decrypt(
        self, key, ct, *, aad=None
    ):  # pragma: no cover - demo only
        raise NotImplementedError

    async def wrap(
        self, kek, *, dek=None, wrap_alg=None, nonce=None
    ):  # pragma: no cover - demo only
        raise NotImplementedError

    async def unwrap(self, kek, wrapped):  # pragma: no cover - demo only
        raise NotImplementedError

    async def seal(
        self, recipient, pt, *, alg=None
    ):  # pragma: no cover - demo only
        raise NotImplementedError

    async def unseal(
        self, recipient_priv, sealed, *, alg=None
    ):  # pragma: no cover - demo only
        raise NotImplementedError

    async def encaps(
        self, recipient, *, alg=None
    ):  # pragma: no cover - demo only
        raise NotImplementedError

    async def decaps(
        self, recipient_priv, encapsulated_key, *, alg=None
    ):  # pragma: no cover - demo only
        raise NotImplementedError


async def main() -> None:
    # Compose two providers that advertise different algorithms.
    chacha = DummyCrypto("chacha", "CHACHA20-POLY1305")
    aes = DummyCrypto("aes", "A256GCM")
    composite = CompositeCrypto([chacha, aes])

    key = KeyRef(
        kid="k",
        version=1,
        type=KeyType.SYMMETRIC,
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=b"\x00" * 32,
    )

    ciphertext = await composite.encrypt(key, b"payload", alg="A256GCM")
    print(f"Selected provider: {ciphertext.ct.decode()}")


if __name__ == "__main__":
    asyncio.run(main())
