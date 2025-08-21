import pytest
from ctypes import c_ubyte

from swarmauri_crypto_sodium import SodiumCrypto
from swarmauri_crypto_sodium.sodium_crypto import (
    _CRYPTO_BOX_PUBLICKEYBYTES,
    _CRYPTO_BOX_SECRETKEYBYTES,
    _CRYPTO_SIGN_PUBLICKEYBYTES,
    _CRYPTO_SIGN_SECRETKEYBYTES,
    _XCHACHA_KEYBYTES,
    _SEAL_ALG,
    _sodium,
)
from swarmauri_core.crypto.types import (
    AEADCiphertext,
    ExportPolicy,
    KeyRef,
    KeyType,
    KeyUse,
    WrappedKey,
)


@pytest.fixture
def sodium_crypto():
    return SodiumCrypto()


def _gen_x25519_keypair():
    lib = _sodium()
    pk = (c_ubyte * _CRYPTO_BOX_PUBLICKEYBYTES)()
    sk = (c_ubyte * _CRYPTO_BOX_SECRETKEYBYTES)()
    lib.crypto_box_keypair(pk, sk)
    return bytes(pk), bytes(sk)


def _gen_ed25519_keypair():
    lib = _sodium()
    pk = (c_ubyte * _CRYPTO_SIGN_PUBLICKEYBYTES)()
    sk = (c_ubyte * _CRYPTO_SIGN_SECRETKEYBYTES)()
    lib.crypto_sign_ed25519_keypair(pk, sk)
    return bytes(pk), bytes(sk)


@pytest.mark.unit
def test_resource_and_type(sodium_crypto):
    assert sodium_crypto.resource == "Crypto"
    assert sodium_crypto.type == "SodiumCrypto"


@pytest.mark.asyncio
async def test_aead_encrypt_decrypt_roundtrip(sodium_crypto):
    sym = KeyRef(
        kid="sym1",
        version=1,
        type=KeyType.SYMMETRIC,
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=b"\x11" * _XCHACHA_KEYBYTES,
    )
    pt = b"hello world"
    ct = await sodium_crypto.encrypt(sym, pt)
    rt = await sodium_crypto.decrypt(sym, ct)
    assert rt == pt


@pytest.mark.asyncio
async def test_sign_and_verify(sodium_crypto):
    pk, sk = _gen_ed25519_keypair()
    signer = KeyRef(
        kid="sig1",
        version=1,
        type=KeyType.ED25519,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=sk,
    )
    verifier = KeyRef(
        kid="sig1",
        version=1,
        type=KeyType.ED25519,
        uses=(KeyUse.VERIFY,),
        export_policy=ExportPolicy.PUBLIC_ONLY,
        public=pk,
    )
    msg = b"message"
    sig = await sodium_crypto.sign(signer, msg)
    ok = await sodium_crypto.verify(verifier, msg, sig)
    assert ok


@pytest.mark.asyncio
async def test_seal_unseal(sodium_crypto):
    pk, sk = _gen_x25519_keypair()
    recipient = KeyRef(
        kid="r1",
        version=1,
        type=KeyType.X25519,
        uses=(KeyUse.SEAL,),
        export_policy=ExportPolicy.PUBLIC_ONLY,
        public=pk,
    )
    priv = KeyRef(
        kid="r1",
        version=1,
        type=KeyType.X25519,
        uses=(KeyUse.UNSEAL,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        public=pk,
        material=sk,
    )
    sealed = await sodium_crypto.seal(recipient, b"secret")
    opened = await sodium_crypto.unseal(priv, sealed)
    assert opened == b"secret"


@pytest.mark.asyncio
async def test_wrap_unwrap(sodium_crypto):
    pk, sk = _gen_x25519_keypair()
    kek_pub = KeyRef(
        kid="kek",
        version=1,
        type=KeyType.X25519,
        uses=(KeyUse.WRAP,),
        export_policy=ExportPolicy.PUBLIC_ONLY,
        public=pk,
    )
    kek_priv = KeyRef(
        kid="kek",
        version=1,
        type=KeyType.X25519,
        uses=(KeyUse.UNWRAP,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        public=pk,
        material=sk,
    )
    wrapped = await sodium_crypto.wrap(kek_pub)
    dek = await sodium_crypto.unwrap(kek_priv, wrapped)
    assert isinstance(dek, bytes)
    assert len(dek) == _XCHACHA_KEYBYTES


@pytest.mark.asyncio
async def test_encrypt_for_many_modes(sodium_crypto):
    pk, sk = _gen_x25519_keypair()
    recipient = KeyRef(
        kid="r1",
        version=1,
        type=KeyType.X25519,
        uses=(KeyUse.UNWRAP, KeyUse.SEAL),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        public=pk,
        material=sk,
    )
    pt = b"multicast"
    # KEM+AEAD mode
    env = await sodium_crypto.encrypt_for_many([recipient], pt)
    wrapped = env.recipients[0]
    cek = await sodium_crypto.unwrap(
        recipient,
        WrappedKey(
            kek_kid=recipient.kid,
            kek_version=recipient.version,
            wrap_alg=wrapped.wrap_alg,
            wrapped=wrapped.wrapped_key,
            nonce=None,
        ),
    )
    sym = KeyRef(
        kid="tmp",
        version=1,
        type=KeyType.SYMMETRIC,
        uses=(KeyUse.DECRYPT,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=cek,
    )
    ct = AEADCiphertext(
        kid="tmp",
        version=1,
        alg=env.enc_alg,
        nonce=env.nonce,
        ct=env.ct,
        tag=env.tag,
        aad=env.aad,
    )
    out = await sodium_crypto.decrypt(sym, ct)
    assert out == pt
    # sealed-style
    env2 = await sodium_crypto.encrypt_for_many([recipient], pt, enc_alg=_SEAL_ALG)
    sealed = env2.recipients[0].wrapped_key
    unsealed = await sodium_crypto.unseal(recipient, sealed)
    assert unsealed == pt
