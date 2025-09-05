import pytest
from pgpy import PGPKey, PGPUID
from pgpy.constants import (
    PubKeyAlgorithm,
    KeyFlags,
    HashAlgorithm,
    SymmetricKeyAlgorithm,
    CompressionAlgorithm,
)

from swarmauri_signing_pgp import PgpEnvelopeSigner


async def _generate_key():
    key = PGPKey.new(PubKeyAlgorithm.RSAEncryptOrSign, 2048)
    uid = PGPUID.new("Test User", email="test@example.com")
    key.add_uid(
        uid,
        usage={KeyFlags.Sign},
        hashes=[HashAlgorithm.SHA256],
        ciphers=[SymmetricKeyAlgorithm.AES256],
        compression=[CompressionAlgorithm.ZLIB],
    )
    return key


@pytest.mark.asyncio
@pytest.mark.i9n
@pytest.mark.test
async def test_sign_and_verify_envelope_json():
    signer = PgpEnvelopeSigner()
    key = await _generate_key()
    env = {"msg": "hi"}
    sigs = await signer.sign_envelope({"kind": "pgpy_key", "priv": key}, env)
    ok = await signer.verify_envelope(env, sigs, opts={"pubkeys": [key.pubkey]})
    assert ok
