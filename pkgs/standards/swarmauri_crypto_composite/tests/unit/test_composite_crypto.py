import pytest
from swarmauri_core.crypto.types import (
    KeyRef,
    KeyType,
    KeyUse,
    ExportPolicy,
    AEADCiphertext,
)
from swarmauri_crypto_composite import CompositeCrypto


class DummyCrypto:
    def __init__(self, alg: str) -> None:
        self.alg = alg
        self.called = False

    def supports(self):
        return {"encrypt": (self.alg,)}

    async def encrypt(
        self,
        key: KeyRef,
        pt: bytes,
        *,
        alg: str | None = None,
        aad: bytes | None = None,
        nonce: bytes | None = None,
    ):
        self.called = True
        return AEADCiphertext(key.kid, key.version, self.alg, b"", b"", b"")


@pytest.mark.asyncio
async def test_encrypt_routes_by_alg():
    key = KeyRef(
        kid="sym1",
        version=1,
        type=KeyType.SYMMETRIC,
        uses=(KeyUse.ENCRYPT,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=b"\x00" * 32,
    )
    a = DummyCrypto("AALG")
    b = DummyCrypto("BALG")
    cc = CompositeCrypto([a, b])
    await cc.encrypt(key, b"data", alg="BALG")
    assert b.called and not a.called
