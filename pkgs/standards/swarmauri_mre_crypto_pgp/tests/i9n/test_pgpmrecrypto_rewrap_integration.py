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


def make_key(email: str) -> PGPKey:
    key = PGPKey.new(PubKeyAlgorithm.RSAEncryptOrSign, 2048)
    uid = PGPUID.new("User", email=email)
    key.add_uid(
        uid,
        usage={KeyFlags.EncryptCommunications},
        hashes=[HashAlgorithm.SHA256],
        ciphers=[SymmetricKeyAlgorithm.AES256],
        compression=[CompressionAlgorithm.ZLIB],
    )
    return key


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_rewrap_add_and_remove_enc_once_headers():
    crypto = PGPMreCrypto()
    key1 = make_key("a@example.com")
    key2 = make_key("b@example.com")
    pub1 = {"kind": "pgpy_pub", "pub": key1.pubkey}
    priv1 = {"kind": "pgpy_priv", "priv": key1}
    pub2 = {"kind": "pgpy_pub", "pub": key2.pubkey}
    priv2 = {"kind": "pgpy_priv", "priv": key2}
    pt = b"integration"

    env = await crypto.encrypt_for_many([pub1], pt)
    env = await crypto.rewrap(env, add=[pub2], opts={"manage_key": priv1})
    assert len(env["recipients"]) == 2
    env = await crypto.rewrap(env, remove=[str(key1.fingerprint)])
    assert len(env["recipients"]) == 1

    rt = await crypto.open_for(priv2, env)
    assert rt == pt
    with pytest.raises(PermissionError):
        await crypto.open_for(priv1, env)
