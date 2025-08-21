import asyncio
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import pytest

from swarmauri_signing_casigner import CASigner
from swarmauri_core.crypto.types import KeyRef, KeyType, KeyUse, ExportPolicy


@pytest.mark.perf
def test_sign_bytes_perf(benchmark):
    signer = CASigner()
    sk = Ed25519PrivateKey.generate()
    key = KeyRef(
        kid="k1",
        version=1,
        type=KeyType.ED25519,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        tags={"crypto_obj": sk},
    )
    payload = b"perf-test"

    async def _sign():
        await signer.sign_bytes(key, payload)

    benchmark(lambda: asyncio.run(_sign()))
