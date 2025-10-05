import ctypes

import pytest

from swarmauri_core.crypto.types import (
    AEADCiphertext,
    ExportPolicy,
    IntegrityError,
    KeyRef,
    KeyType,
    KeyUse,
    MultiRecipientEnvelope,
    UnsupportedAlgorithm,
    WrappedKey,
)

try:
    from swarmauri_crypto_sodium import SodiumCrypto
    from swarmauri_crypto_sodium.SodiumCrypto import (
        _CRYPTO_BOX_PUBLICKEYBYTES,
        _CRYPTO_BOX_SECRETKEYBYTES,
        _sodium,
    )
except Exception as exc:  # pragma: no cover - handled by pytest.skip
    pytest.skip(
        f"swarmauri_crypto_sodium import failed: {exc}", allow_module_level=True
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


@pytest.fixture
def symmetric_key():
    return KeyRef(
        kid="sym-fixture",
        version=1,
        type=KeyType.SYMMETRIC,
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=b"\x22" * 32,
    )


@pytest.mark.unit
def test_ubc_resource(sodium_crypto):
    assert sodium_crypto.resource == "Crypto"


@pytest.mark.unit
def test_ubc_type(sodium_crypto):
    assert sodium_crypto.type == "SodiumCrypto"


@pytest.mark.unit
def test_supports_declares_expected_capabilities(sodium_crypto):
    assert sodium_crypto.supports() == {
        "encrypt": ("XCHACHA20-POLY1305",),
        "decrypt": ("XCHACHA20-POLY1305",),
        "wrap": ("X25519-SEAL-WRAP",),
        "unwrap": ("X25519-SEAL-WRAP",),
        "seal": ("X25519-SEALEDBOX",),
        "unseal": ("X25519-SEALEDBOX",),
    }


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
async def test_encrypt_rejects_unknown_algorithm(sodium_crypto, symmetric_key):
    with pytest.raises(UnsupportedAlgorithm):
        await sodium_crypto.encrypt(symmetric_key, b"data", alg="AES256-GCM")


@pytest.mark.asyncio
async def test_encrypt_rejects_incorrect_nonce_length(sodium_crypto, symmetric_key):
    with pytest.raises(IntegrityError):
        await sodium_crypto.encrypt(
            symmetric_key,
            b"payload",
            nonce=b"short",
        )


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
async def test_wrap_rejects_unknown_algorithm(sodium_crypto, x25519_keys):
    pk, _ = x25519_keys
    kek = KeyRef(
        kid="x2",
        version=1,
        type=KeyType.X25519,
        uses=(KeyUse.WRAP,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        public=pk,
    )
    with pytest.raises(UnsupportedAlgorithm):
        await sodium_crypto.wrap(kek, wrap_alg="RSA-OAEP")


@pytest.mark.asyncio
async def test_wrap_requires_public_key_material(sodium_crypto):
    kek = KeyRef(
        kid="x3",
        version=1,
        type=KeyType.X25519,
        uses=(KeyUse.WRAP,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    )
    with pytest.raises(ValueError):
        await sodium_crypto.wrap(kek)


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
async def test_seal_rejects_unknown_algorithm(sodium_crypto, x25519_keys):
    pk, _ = x25519_keys
    recipient = KeyRef(
        kid="r2",
        version=1,
        type=KeyType.X25519,
        uses=(KeyUse.WRAP,),
        export_policy=ExportPolicy.PUBLIC_ONLY,
        public=pk,
    )
    with pytest.raises(UnsupportedAlgorithm):
        await sodium_crypto.seal(recipient, b"msg", alg="RSA")


@pytest.mark.asyncio
async def test_unseal_rejects_unknown_algorithm(sodium_crypto, x25519_keys):
    pk, sk = x25519_keys
    recipient = KeyRef(
        kid="r3",
        version=1,
        type=KeyType.X25519,
        uses=(KeyUse.UNWRAP,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        public=pk,
        material=sk,
    )
    sealed = await sodium_crypto.seal(
        KeyRef(
            kid="r3",
            version=1,
            type=KeyType.X25519,
            uses=(KeyUse.WRAP,),
            export_policy=ExportPolicy.PUBLIC_ONLY,
            public=pk,
        ),
        b"secret",
    )
    with pytest.raises(UnsupportedAlgorithm):
        await sodium_crypto.unseal(recipient, sealed, alg="WRONG")


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
            nonce=env.recipients[0].nonce,
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


@pytest.mark.asyncio
async def test_encrypt_for_many_sealed_variant(sodium_crypto, x25519_keys):
    pk, _ = x25519_keys
    recipients = [
        KeyRef(
            kid="r4",
            version=1,
            type=KeyType.X25519,
            uses=(KeyUse.WRAP,),
            export_policy=ExportPolicy.PUBLIC_ONLY,
            public=pk,
        ),
        KeyRef(
            kid="r5",
            version=1,
            type=KeyType.X25519,
            uses=(KeyUse.WRAP,),
            export_policy=ExportPolicy.PUBLIC_ONLY,
            public=pk,
        ),
    ]
    env = await sodium_crypto.encrypt_for_many(recipients, b"sealed", enc_alg="X25519-SEALEDBOX")
    assert isinstance(env, MultiRecipientEnvelope)
    assert env.enc_alg == "X25519-SEALEDBOX"
    assert all(info.wrap_alg == "X25519-SEALEDBOX" for info in env.recipients)
    assert env.nonce == b""
    assert env.ct == b""
    assert env.tag == b""


@pytest.mark.asyncio
async def test_encrypt_for_many_rejects_unknown_enc_alg(sodium_crypto, x25519_keys):
    pk, sk = x25519_keys
    recipient = KeyRef(
        kid="r6",
        version=1,
        type=KeyType.X25519,
        uses=(KeyUse.WRAP, KeyUse.UNWRAP),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        public=pk,
        material=sk,
    )
    with pytest.raises(UnsupportedAlgorithm):
        await sodium_crypto.encrypt_for_many([recipient], b"data", enc_alg="AES256-GCM")


@pytest.mark.asyncio
async def test_encrypt_for_many_rejects_unknown_wrap_alg(sodium_crypto, x25519_keys):
    pk, sk = x25519_keys
    recipient = KeyRef(
        kid="r7",
        version=1,
        type=KeyType.X25519,
        uses=(KeyUse.WRAP, KeyUse.UNWRAP),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        public=pk,
        material=sk,
    )
    with pytest.raises(UnsupportedAlgorithm):
        await sodium_crypto.encrypt_for_many(
            [recipient],
            b"data",
            enc_alg="XCHACHA20-POLY1305",
            recipient_wrap_alg="RSA-OAEP",
        )


@pytest.mark.asyncio
async def test_decrypt_rejects_unknown_algorithm(sodium_crypto, symmetric_key):
    ciphertext = AEADCiphertext(
        kid="sym-fixture",
        version=1,
        alg="AES256-GCM",
        nonce=b"\x00" * 24,
        ct=b"",
        tag=b"\x00" * 16,
    )
    with pytest.raises(UnsupportedAlgorithm):
        await sodium_crypto.decrypt(symmetric_key, ciphertext)


@pytest.mark.asyncio
async def test_decrypt_rejects_invalid_nonce_length(sodium_crypto, symmetric_key):
    ct = await sodium_crypto.encrypt(symmetric_key, b"nonce-check")
    bad_ct = AEADCiphertext(
        kid=ct.kid,
        version=ct.version,
        alg=ct.alg,
        nonce=ct.nonce[:-1],
        ct=ct.ct,
        tag=ct.tag,
        aad=ct.aad,
    )
    with pytest.raises(IntegrityError):
        await sodium_crypto.decrypt(symmetric_key, bad_ct)


@pytest.mark.asyncio
async def test_decrypt_raises_on_integrity_failure(sodium_crypto, symmetric_key):
    ct = await sodium_crypto.encrypt(symmetric_key, b"tamper")
    tampered = AEADCiphertext(
        kid=ct.kid,
        version=ct.version,
        alg=ct.alg,
        nonce=ct.nonce,
        ct=ct.ct,
        tag=bytes([ct.tag[0] ^ 0x01]) + ct.tag[1:],
        aad=ct.aad,
    )
    with pytest.raises(IntegrityError):
        await sodium_crypto.decrypt(symmetric_key, tampered)


@pytest.mark.asyncio
async def test_unwrap_rejects_unknown_algorithm(sodium_crypto, x25519_keys):
    pk, sk = x25519_keys
    kek = KeyRef(
        kid="x4",
        version=1,
        type=KeyType.X25519,
        uses=(KeyUse.UNWRAP,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        public=pk,
        material=sk,
    )
    wrapped = await sodium_crypto.wrap(
        KeyRef(
            kid="x4",
            version=1,
            type=KeyType.X25519,
            uses=(KeyUse.WRAP,),
            export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
            public=pk,
        ),
    )
    bad_wrapped = WrappedKey(
        kek_kid=wrapped.kek_kid,
        kek_version=wrapped.kek_version,
        wrap_alg="RSA-OAEP",
        wrapped=wrapped.wrapped,
        nonce=wrapped.nonce,
    )
    with pytest.raises(UnsupportedAlgorithm):
        await sodium_crypto.unwrap(kek, bad_wrapped)


@pytest.mark.asyncio
async def test_unwrap_requires_secret_key_material(sodium_crypto, x25519_keys):
    pk, _ = x25519_keys
    wrapping_kek = KeyRef(
        kid="x5",
        version=1,
        type=KeyType.X25519,
        uses=(KeyUse.WRAP,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        public=pk,
    )
    wrapped = await sodium_crypto.wrap(wrapping_kek)
    with pytest.raises(ValueError):
        await sodium_crypto.unwrap(wrapping_kek, wrapped)


@pytest.mark.asyncio
async def test_unseal_requires_secret_key_material(sodium_crypto, x25519_keys):
    pk, sk = x25519_keys
    recipient_pub = KeyRef(
        kid="r8",
        version=1,
        type=KeyType.X25519,
        uses=(KeyUse.WRAP,),
        export_policy=ExportPolicy.PUBLIC_ONLY,
        public=pk,
    )
    sealed = await sodium_crypto.seal(recipient_pub, b"needs-secret")
    recipient_priv_missing = KeyRef(
        kid="r8",
        version=1,
        type=KeyType.X25519,
        uses=(KeyUse.UNWRAP,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        public=pk,
    )
    with pytest.raises(ValueError):
        await sodium_crypto.unseal(recipient_priv_missing, sealed)


@pytest.mark.asyncio
async def test_unseal_requires_matching_secret_key(sodium_crypto, x25519_keys):
    pk, sk = x25519_keys
    other_pk_buf = (ctypes.c_ubyte * _CRYPTO_BOX_PUBLICKEYBYTES)()
    other_sk_buf = (ctypes.c_ubyte * _CRYPTO_BOX_SECRETKEYBYTES)()
    rc = _sodium().crypto_box_keypair(other_pk_buf, other_sk_buf)
    assert rc == 0
    other_pk = bytes(other_pk_buf)
    other_sk = bytes(other_sk_buf)
    recipient_pub = KeyRef(
        kid="r9",
        version=1,
        type=KeyType.X25519,
        uses=(KeyUse.WRAP,),
        export_policy=ExportPolicy.PUBLIC_ONLY,
        public=pk,
    )
    sealed = await sodium_crypto.seal(recipient_pub, b"mismatch")
    wrong_recipient = KeyRef(
        kid="r9",
        version=1,
        type=KeyType.X25519,
        uses=(KeyUse.UNWRAP,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        public=other_pk,
        material=other_sk,
    )
    with pytest.raises(IntegrityError):
        await sodium_crypto.unseal(wrong_recipient, sealed)


@pytest.mark.asyncio
async def test_encrypt_for_many_requires_wrap_key_material(sodium_crypto, x25519_keys):
    pk, _ = x25519_keys
    recipient = KeyRef(
        kid="r10",
        version=1,
        type=KeyType.X25519,
        uses=(KeyUse.WRAP,),
        export_policy=ExportPolicy.PUBLIC_ONLY,
        public=pk,
    )
    env = await sodium_crypto.encrypt_for_many([recipient], b"no-secret", enc_alg="X25519-SEALEDBOX")
    assert env.recipients[0].wrapped_key != b""


@pytest.mark.asyncio
async def test_encrypt_for_many_requires_valid_wrap_key(sodium_crypto, x25519_keys):
    pk, sk = x25519_keys
    recipient = KeyRef(
        kid="r11",
        version=1,
        type=KeyType.X25519,
        uses=(KeyUse.WRAP, KeyUse.UNWRAP),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        public=pk,
        material=sk,
    )
    env = await sodium_crypto.encrypt_for_many([recipient], b"wrap-check")
    assert env.recipients[0].wrap_alg == "X25519-SEAL-WRAP"


@pytest.mark.asyncio
async def test_decrypt_uses_explicit_aad_when_provided(sodium_crypto, symmetric_key):
    ct = await sodium_crypto.encrypt(symmetric_key, b"aad-data", aad=b"orig")
    new_aad = b"override"
    decrypted = await sodium_crypto.decrypt(symmetric_key, ct, aad=new_aad)
    assert decrypted == b"aad-data"


@pytest.mark.asyncio
async def test_sign_not_implemented(sodium_crypto, symmetric_key):
    with pytest.raises(UnsupportedAlgorithm):
        await sodium_crypto.sign(symmetric_key, b"message")


@pytest.mark.asyncio
async def test_verify_not_implemented(sodium_crypto, symmetric_key):
    with pytest.raises(UnsupportedAlgorithm):
        await sodium_crypto.verify(symmetric_key, b"message", b"sig")
