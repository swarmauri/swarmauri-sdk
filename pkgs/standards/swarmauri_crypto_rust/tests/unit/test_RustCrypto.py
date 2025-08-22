import pytest
import secrets
from swarmauri_core.crypto.types import (
    ExportPolicy,
    KeyRef,
    KeyType,
    KeyUse,
    AEADCiphertext,
    WrappedKey,
)

from swarmauri_crypto_rust import RustCrypto


@pytest.fixture
def rust_crypto():
    return RustCrypto()


@pytest.fixture
def symmetric_key():
    return KeyRef(
        kid="test-sym",
        version=1,
        type=KeyType.SYMMETRIC,
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=secrets.token_bytes(32),
    )


@pytest.fixture
def x25519_key():
    # Generate a simple X25519-like key (32 bytes for demo)
    private_key = secrets.token_bytes(32)
    public_key = secrets.token_bytes(32)  # In real X25519, this would be derived

    return KeyRef(
        kid="test-x25519",
        version=1,
        type=KeyType.X25519,
        uses=(KeyUse.WRAP, KeyUse.UNWRAP),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=private_key,
        public=public_key,
    )


@pytest.mark.unit
def test_ubc_resource(rust_crypto):
    assert rust_crypto.resource == "Crypto"


@pytest.mark.unit
def test_ubc_type(rust_crypto):
    assert rust_crypto.type == "RustCrypto"


@pytest.mark.unit
def test_serialization(rust_crypto):
    assert (
        rust_crypto.id
        == RustCrypto.model_validate_json(rust_crypto.model_dump_json()).id
    )


@pytest.mark.unit
def test_supports(rust_crypto):
    supports = rust_crypto.supports()
    assert "encrypt" in supports
    assert "decrypt" in supports
    assert "wrap" in supports
    assert "unwrap" in supports


@pytest.mark.unit
def test_version_info(rust_crypto):
    version_info = rust_crypto.get_version_info()
    assert "rust_crypto_version" in version_info
    assert "ring_version" in version_info
    assert "backend" in version_info


@pytest.mark.unit
def test_generate_key(rust_crypto):
    key_32 = rust_crypto.generate_key(32)
    assert len(key_32) == 32
    assert isinstance(key_32, bytes)

    key_16 = rust_crypto.generate_key(16)
    assert len(key_16) == 16

    # Keys should be different
    assert key_32 != key_16[:32]


@pytest.mark.asyncio
async def test_aead_encrypt_decrypt_roundtrip(rust_crypto, symmetric_key):
    plaintext = b"Hello, Rust crypto world!"

    # Test encryption
    ciphertext = await rust_crypto.encrypt(symmetric_key, plaintext)

    assert isinstance(ciphertext, AEADCiphertext)
    assert ciphertext.kid == symmetric_key.kid
    assert ciphertext.version == symmetric_key.version
    assert ciphertext.alg == "CHACHA20-POLY1305"
    assert len(ciphertext.nonce) == 12
    assert len(ciphertext.ct) == len(plaintext)
    assert len(ciphertext.tag) == 16

    # Test decryption
    decrypted = await rust_crypto.decrypt(symmetric_key, ciphertext)
    assert decrypted == plaintext


@pytest.mark.asyncio
async def test_aead_encrypt_with_aad(rust_crypto, symmetric_key):
    plaintext = b"Secret message"
    aad = b"Additional authenticated data"

    ciphertext = await rust_crypto.encrypt(symmetric_key, plaintext, aad=aad)
    decrypted = await rust_crypto.decrypt(symmetric_key, ciphertext, aad=aad)

    assert decrypted == plaintext
    assert ciphertext.aad == aad


@pytest.mark.asyncio
async def test_aead_encrypt_with_nonce(rust_crypto, symmetric_key):
    plaintext = b"Message with custom nonce"
    nonce = secrets.token_bytes(12)

    ciphertext = await rust_crypto.encrypt(symmetric_key, plaintext, nonce=nonce)
    decrypted = await rust_crypto.decrypt(symmetric_key, ciphertext)

    assert decrypted == plaintext
    assert ciphertext.nonce == nonce


@pytest.mark.asyncio
async def test_wrap_unwrap_roundtrip(rust_crypto, x25519_key):
    dek = secrets.token_bytes(32)

    # Test wrapping
    wrapped = await rust_crypto.wrap(x25519_key, dek=dek)

    assert isinstance(wrapped, WrappedKey)
    assert wrapped.kek_kid == x25519_key.kid
    assert wrapped.kek_version == x25519_key.version
    assert wrapped.wrap_alg == "ECDH-ES+A256KW"
    assert len(wrapped.wrapped) >= 32  # Should include padding

    # Test unwrapping
    unwrapped = await rust_crypto.unwrap(x25519_key, wrapped)
    assert unwrapped == dek


@pytest.mark.asyncio
async def test_seal_unseal_roundtrip(rust_crypto, x25519_key):
    plaintext = b"Top secret sealed message"

    # Test sealing
    sealed = await rust_crypto.seal(x25519_key, plaintext)
    assert isinstance(sealed, bytes)
    assert len(sealed) > len(plaintext)  # Should be larger due to encryption overhead

    # Test unsealing
    unsealed = await rust_crypto.unseal(x25519_key, sealed)
    assert unsealed == plaintext


@pytest.mark.asyncio
async def test_encrypt_for_many_seal_style(rust_crypto, x25519_key):
    plaintext = b"Multi-recipient message"
    recipients = [x25519_key]

    envelope = await rust_crypto.encrypt_for_many(
        recipients, plaintext, enc_alg="X25519-SEAL"
    )

    assert envelope.enc_alg == "X25519-SEAL"
    assert len(envelope.recipients) == 1
    assert envelope.recipients[0].kid == x25519_key.kid
    assert envelope.recipients[0].wrap_alg == "X25519-SEAL"
    assert len(envelope.recipients[0].wrapped_key) > 0


@pytest.mark.asyncio
async def test_encrypt_for_many_kem_aead(rust_crypto, x25519_key):
    plaintext = b"KEM+AEAD message"
    recipients = [x25519_key]

    envelope = await rust_crypto.encrypt_for_many(
        recipients, plaintext, enc_alg="CHACHA20-POLY1305"
    )

    assert envelope.enc_alg == "CHACHA20-POLY1305"
    assert len(envelope.recipients) == 1
    assert envelope.recipients[0].kid == x25519_key.kid
    assert envelope.recipients[0].wrap_alg == "ECDH-ES+A256KW"
    assert len(envelope.ct) > 0
    assert len(envelope.tag) > 0
    assert len(envelope.nonce) > 0

    # Test reconstruction
    wrapped_key = WrappedKey(
        kek_kid=envelope.recipients[0].kid,
        kek_version=envelope.recipients[0].version,
        wrap_alg=envelope.recipients[0].wrap_alg,
        wrapped=envelope.recipients[0].wrapped_key,
    )

    cek_bytes = await rust_crypto.unwrap(x25519_key, wrapped_key)

    cek = KeyRef(
        kid="cek",
        version=1,
        type=KeyType.SYMMETRIC,
        uses=(KeyUse.DECRYPT,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=cek_bytes,
    )

    aead_ct = AEADCiphertext(
        kid="cek",
        version=1,
        alg=envelope.enc_alg,
        nonce=envelope.nonce,
        ct=envelope.ct,
        tag=envelope.tag,
        aad=envelope.aad,
    )

    decrypted = await rust_crypto.decrypt(cek, aead_ct)
    assert decrypted == plaintext


@pytest.mark.asyncio
async def test_error_handling_invalid_key_size(rust_crypto):
    invalid_key = KeyRef(
        kid="invalid",
        version=1,
        type=KeyType.SYMMETRIC,
        uses=(KeyUse.ENCRYPT,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=b"too_short",  # Invalid length
    )

    with pytest.raises(Exception):  # Should raise IntegrityError
        await rust_crypto.encrypt(invalid_key, b"test")


@pytest.mark.asyncio
async def test_error_handling_missing_key_material(rust_crypto):
    key_without_material = KeyRef(
        kid="no-material",
        version=1,
        type=KeyType.SYMMETRIC,
        uses=(KeyUse.ENCRYPT,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=None,
    )

    with pytest.raises(Exception):  # Should raise IntegrityError
        await rust_crypto.encrypt(key_without_material, b"test")


@pytest.mark.asyncio
async def test_error_handling_wrong_algorithm(rust_crypto, symmetric_key):
    from swarmauri_core.crypto.types import UnsupportedAlgorithm

    with pytest.raises(UnsupportedAlgorithm):
        await rust_crypto.encrypt(symmetric_key, b"test", alg="UNSUPPORTED-ALG")
