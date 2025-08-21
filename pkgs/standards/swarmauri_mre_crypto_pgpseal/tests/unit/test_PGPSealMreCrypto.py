import pytest
from pgpy import PGPKey, PGPUID
from pgpy.constants import (
    PubKeyAlgorithm,
    KeyFlags,
    HashAlgorithm,
    SymmetricKeyAlgorithm,
    CompressionAlgorithm,
)

from swarmauri_mre_crypto_pgpseal import PGPSealMreCrypto


def _generate_key() -> PGPKey:
    key = PGPKey.new(PubKeyAlgorithm.RSAEncryptOrSign, 2048)
    uid = PGPUID.new("Test", email="test@example.com")
    key.add_uid(
        uid,
        usage={KeyFlags.EncryptCommunications},
        hashes=[HashAlgorithm.SHA256],
        ciphers=[SymmetricKeyAlgorithm.AES256],
        compression=[CompressionAlgorithm.ZLIB],
    )
    return key


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.test
async def test_encrypt_and_open_roundtrip():
    key = _generate_key()
    crypto = PGPSealMreCrypto()
    recipients = [{"kind": "pgpy_pub", "pub": key.pubkey}]
    env = await crypto.encrypt_for_many(recipients, b"hello")
    pt = await crypto.open_for({"kind": "pgpy_priv", "priv": key}, env)
    assert pt == b"hello"
