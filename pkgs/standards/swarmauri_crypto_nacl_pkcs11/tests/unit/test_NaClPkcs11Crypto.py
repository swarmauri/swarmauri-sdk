import pytest
from nacl.public import PrivateKey

from swarmauri_crypto_nacl_pkcs11 import NaClPkcs11Crypto
from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse


@pytest.fixture
def crypto():
    return NaClPkcs11Crypto()


@pytest.mark.unit
def test_resource_and_type(crypto):
    assert crypto.resource == "Crypto"
    assert crypto.type == "NaClPkcs11Crypto"


@pytest.mark.asyncio
async def test_aead_encrypt_decrypt_roundtrip(crypto):
    key = KeyRef(
        kid="sym1",
        version=1,
        type=KeyType.SYMMETRIC,
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=b"\x11" * 32,
    )
    pt = b"hello world"
    ct = await crypto.encrypt(key, pt)
    rt = await crypto.decrypt(key, ct)
    assert rt == pt


@pytest.mark.asyncio
async def test_seal_unseal(crypto):
    priv = PrivateKey.generate()
    pub_ref = KeyRef(
        kid="x1",
        version=1,
        type=KeyType.X25519,
        uses=(KeyUse.ENCRYPT,),
        export_policy=ExportPolicy.PUBLIC_ONLY,
        public=priv.public_key.encode(),
    )
    priv_ref = KeyRef(
        kid="x1",
        version=1,
        type=KeyType.X25519,
        uses=(KeyUse.DECRYPT,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=priv.encode(),
        public=priv.public_key.encode(),
    )
    pt = b"sealed secret"
    sealed = await crypto.seal(pub_ref, pt)
    opened = await crypto.unseal(priv_ref, sealed)
    assert opened == pt


@pytest.mark.asyncio
async def test_encrypt_for_many(crypto):
    priv = PrivateKey.generate()
    pub_ref = KeyRef(
        kid="x1",
        version=1,
        type=KeyType.X25519,
        uses=(KeyUse.ENCRYPT,),
        export_policy=ExportPolicy.PUBLIC_ONLY,
        public=priv.public_key.encode(),
    )
    env = await crypto.encrypt_for_many([pub_ref], b"hi")
    assert env.enc_alg == "X25519-SEALEDBOX"
    assert env.nonce == env.ct == env.tag == b""
    assert len(env.recipients) == 1
    info = env.recipients[0]
    assert info.kid == "x1"
    assert info.wrap_alg == "X25519-SEALEDBOX"
    assert info.wrapped_key
