import pgpy
import pytest
from swarmauri_mre_crypto_pgp import PGPMreCrypto


def _generate_keypair():
    key = pgpy.PGPKey.new(pgpy.constants.PubKeyAlgorithm.RSAEncryptOrSign, 1024)
    uid = pgpy.PGPUID.new("Test", email="test@example.com")
    key.add_uid(
        uid,
        usage={pgpy.constants.KeyFlags.EncryptCommunications},
        hashes=[pgpy.constants.HashAlgorithm.SHA256],
        ciphers=[pgpy.constants.SymmetricKeyAlgorithm.AES256],
        compression=[pgpy.constants.CompressionAlgorithm.Uncompressed],
    )
    return {"kind": "pgpy_pub", "pub": key.pubkey}, {"kind": "pgpy_priv", "priv": key}


@pytest.mark.asyncio
@pytest.mark.i9n
async def test_encrypt_open_roundtrip():
    pub, priv = _generate_keypair()
    crypto = PGPMreCrypto()
    env = await crypto.encrypt_for_many([pub], b"hello")
    pt = await crypto.open_for(priv, env)
    assert pt == b"hello"
