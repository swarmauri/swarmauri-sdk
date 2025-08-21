import pytest
from pgpy import PGPKey, PGPUID
from pgpy.constants import (
    PubKeyAlgorithm,
    KeyFlags,
    HashAlgorithm,
    SymmetricKeyAlgorithm,
    CompressionAlgorithm,
)

from swarmauri_signing_pgp import PgpEnvelopeSigner


async def _generate_key():
    key = PGPKey.new(PubKeyAlgorithm.RSAEncryptOrSign, 2048)
    uid = PGPUID.new("Test User", email="test@example.com")
    key.add_uid(
        uid,
        usage={KeyFlags.Sign},
        hashes=[HashAlgorithm.SHA256],
        ciphers=[SymmetricKeyAlgorithm.AES256],
        compression=[CompressionAlgorithm.ZLIB],
    )
    return key


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.test
async def test_sign_and_verify_bytes():
    signer = PgpEnvelopeSigner()
    key = await _generate_key()
    key_ref = {"kind": "pgpy_key", "priv": key}
    payload = b"hello"

    sigs = await signer.sign_bytes(key_ref, payload)
    assert await signer.verify_bytes(payload, sigs, opts={"pubkeys": [key.pubkey]})


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.test
async def test_sign_and_verify_envelope_cbor_optional():
    pytest.importorskip("cbor2")
    signer = PgpEnvelopeSigner()
    key = await _generate_key()
    key_ref = {"kind": "pgpy_key", "priv": key}
    env = {"foo": 1}

    sigs = await signer.sign_envelope(key_ref, env, canon="cbor")
    assert await signer.verify_envelope(
        env, sigs, canon="cbor", opts={"pubkeys": [key.pubkey]}
    )
