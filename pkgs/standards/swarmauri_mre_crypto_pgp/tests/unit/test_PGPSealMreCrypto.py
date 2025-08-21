
import pytest
from pgpy import PGPKey, PGPUID
from pgpy.constants import (
    CompressionAlgorithm,
    HashAlgorithm,
    KeyFlags,
    PubKeyAlgorithm,
    SymmetricKeyAlgorithm,
)

from swarmauri_mre_crypto_pgp import PGPSealMreCrypto


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


@pytest.fixture
def pgp_keys():
    key = generate_key()
    return {"kind": "pgpy_pub", "pub": key.pubkey}, {"kind": "pgpy_priv", "priv": key}


@pytest.fixture
def crypto():
    return PGPSealMreCrypto()


@pytest.mark.unit
def test_resource_and_type(crypto):
    assert crypto.resource == "Crypto"
    assert crypto.type == "PGPSealMreCrypto"


@pytest.mark.unit
def test_serialization(crypto):
    assert (
        crypto.id == PGPSealMreCrypto.model_validate_json(crypto.model_dump_json()).id
    )


@pytest.mark.asyncio
async def test_encrypt_open_roundtrip(crypto, pgp_keys):
    pub_ref, priv_ref = pgp_keys
    pt = b"hello"
    env = await crypto.encrypt_for_many([pub_ref], pt)
    rt = await crypto.open_for(priv_ref, env)
    assert rt == pt
