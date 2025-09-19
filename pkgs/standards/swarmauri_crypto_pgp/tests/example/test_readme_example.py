import pytest

from swarmauri_crypto_pgp import PGPCrypto
from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse


@pytest.mark.asyncio
@pytest.mark.example
async def test_readme_quickstart_example() -> None:
    crypto = PGPCrypto()

    sym = KeyRef(
        kid="sym1",
        version=1,
        type=KeyType.SYMMETRIC,
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=b"\x00" * 32,
    )

    ct = await crypto.encrypt(sym, b"hello OpenPGP")
    pt = await crypto.decrypt(sym, ct)

    assert pt == b"hello OpenPGP"
