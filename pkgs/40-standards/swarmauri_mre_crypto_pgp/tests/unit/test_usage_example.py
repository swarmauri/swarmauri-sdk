import pytest
from pgpy import PGPKey, PGPUID
from pgpy.constants import (
    CompressionAlgorithm,
    HashAlgorithm,
    KeyFlags,
    PubKeyAlgorithm,
    SymmetricKeyAlgorithm,
)

from swarmauri_mre_crypto_pgp import PGPMreCrypto


def generate_key() -> PGPKey:
    key = PGPKey.new(PubKeyAlgorithm.RSAEncryptOrSign, 2048)
    uid = PGPUID.new("Test User", email="test@example.com")
    key.add_uid(
        uid,
        usage={KeyFlags.EncryptCommunications},
        hashes=[HashAlgorithm.SHA256],
        ciphers=[SymmetricKeyAlgorithm.AES256],
        compression=[CompressionAlgorithm.ZLIB],
    )
    return key


@pytest.mark.example
@pytest.mark.unit
@pytest.mark.asyncio
async def test_readme_usage_example():
    key = generate_key()
    pub_ref = {"kind": "pgpy_pub", "pub": key.pubkey}
    priv_ref = {"kind": "pgpy_priv", "priv": key}
    mre = PGPMreCrypto()
    pt = b"hello"
    env = await mre.encrypt_for_many([pub_ref], pt)
    rt = await mre.open_for(priv_ref, env)
    assert rt == pt
