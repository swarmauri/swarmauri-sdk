import ctypes
import pytest
from swarmauri_core.crypto.types import (
    ExportPolicy,
    KeyRef,
    KeyType,
    KeyUse,
    AEADCiphertext,
    WrappedKey,
)

from swarmauri_crypto_sodium import SodiumCrypto
from swarmauri_crypto_sodium.SodiumCrypto import (
    _CRYPTO_BOX_PUBLICKEYBYTES,
    _CRYPTO_BOX_SECRETKEYBYTES,
    _sodium,
)


@pytest.fixture
def sodium_crypto():
    return SodiumCrypto()


@pytest.fixture
def x25519_keys():
    pk = (ctypes.c_ubyte * _CRYPTO_BOX_PUBLICKEYBYTES)()
    sk = (ctypes.c_ubyte * _CRYPTO_BOX_SECRETKEYBYTES)()
    rc = _sodium().crypto_box_keypair(pk, sk)
    assert rc == 0
    return bytes(pk), bytes(sk)


@pytest.mark.unit
def test_ubc_resource(sodium_crypto):
    assert sodium_crypto.resource == "Crypto"


@pytest.mark.unit
def test_ubc_type(sodium_crypto):
    assert sodium_crypto.type == "SodiumCrypto"


@pytest.mark.unit
def test_serialization(sodium_crypto):
    assert (
        sodium_crypto.id
        == SodiumCrypto.model_validate_json(sodium_crypto.model_dump_json()).id
    )


@pytest.mark.asyncio
async def test_aead_encrypt_decrypt_roundtrip(sodium_crypto):
    sym = KeyRef(
        kid="sym1",
        version=1,
        type=KeyType.SYMMETRIC,
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=b"\x11" * 32,
    )
    pt = b"hello world"
    ct = await sodium_crypto.encrypt(sym, pt)
    rt = await sodium_crypto.decrypt(sym, ct)
    assert rt == pt


@pytest.mark.asyncio
async def test_wrap_unwrap(sodium_crypto, x25519_keys):
    pk, sk = x25519_keys
    kek = KeyRef(
        kid="x1",
        version=1,
        type=KeyType.X25519,
        uses=(KeyUse.WRAP, KeyUse.UNWRAP),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        public=pk,
        material=sk,
    )
    dek = b"\x01" * 32
    wrapped = await sodium_crypto.wrap(kek, dek=dek)
    unwrapped = await sodium_crypto.unwrap(kek, wrapped)
    assert unwrapped == dek


@pytest.mark.asyncio
async def test_seal_unseal(sodium_crypto, x25519_keys):
    pk, sk = x25519_keys
    recipient_pub = KeyRef(
        kid="r1",
        version=1,
        type=KeyType.X25519,
        uses=(KeyUse.WRAP,),
        export_policy=ExportPolicy.PUBLIC_ONLY,
        public=pk,
    )
    recipient_priv = KeyRef(
        kid="r1",
        version=1,
        type=KeyType.X25519,
        uses=(KeyUse.UNWRAP,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        public=pk,
        material=sk,
    )
    sealed = await sodium_crypto.seal(recipient_pub, b"top secret")
    opened = await sodium_crypto.unseal(recipient_priv, sealed)
    assert opened == b"top secret"


@pytest.mark.asyncio
async def test_encrypt_for_many_kem_aead(sodium_crypto, x25519_keys):
    pk, sk = x25519_keys
    recipient = KeyRef(
        kid="r1",
        version=1,
        type=KeyType.X25519,
        uses=(KeyUse.WRAP, KeyUse.UNWRAP),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        public=pk,
        material=sk,
    )
    env = await sodium_crypto.encrypt_for_many([recipient], b"secret data")
    assert env.enc_alg == "XCHACHA20-POLY1305"
    assert env.ct and env.tag
    assert len(env.recipients) == 1
    cek = await sodium_crypto.unwrap(
        recipient,
        WrappedKey(
            kek_kid=recipient.kid,
            kek_version=recipient.version,
            wrap_alg="X25519-SEAL-WRAP",
            wrapped=env.recipients[0].wrapped_key,
        ),
    )
    sym = KeyRef(
        kid="cek",
        version=1,
        type=KeyType.SYMMETRIC,
        uses=(KeyUse.DECRYPT,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=cek,
    )
    pt = await sodium_crypto.decrypt(
        sym,
        AEADCiphertext(
            kid="cek",
            version=1,
            alg=env.enc_alg,
            nonce=env.nonce,
            ct=env.ct,
            tag=env.tag,
            aad=env.aad,
        ),
    )
    assert pt == b"secret data"
