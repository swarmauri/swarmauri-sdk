import asyncio
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from swarmauri_signing_casigner import CASigner
from swarmauri_core.crypto.types import KeyRef, KeyType, KeyUse, ExportPolicy


async def _sign_and_verify() -> bool:
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
    payload = b"unit-test"
    sigs = await signer.sign_bytes(key, payload)
    pk = sk.public_key()
    ok = await signer.verify_bytes(payload, sigs, opts={"pubkeys": [pk]})
    return ok


def test_sign_and_verify_unit():
    assert asyncio.run(_sign_and_verify())
