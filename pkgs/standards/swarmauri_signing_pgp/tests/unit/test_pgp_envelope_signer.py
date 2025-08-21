import asyncio

import pgpy
import pytest

from swarmauri_signing_pgp import PgpEnvelopeSigner


@pytest.fixture
def signer() -> PgpEnvelopeSigner:
    return PgpEnvelopeSigner()


@pytest.fixture
def key() -> pgpy.PGPKey:
    key = pgpy.PGPKey.new(pgpy.constants.PubKeyAlgorithm.RSAEncryptOrSign, 2048)
    uid = pgpy.PGPUID.new("Test", email="test@example.com")
    key.add_uid(
        uid,
        usage={pgpy.constants.KeyFlags.Sign},
        hashes=[pgpy.constants.HashAlgorithm.SHA256],
        ciphers=[pgpy.constants.SymmetricKeyAlgorithm.AES256],
        compression=[pgpy.constants.CompressionAlgorithm.ZLIB],
    )
    return key


@pytest.mark.unit
@pytest.mark.asyncio
async def test_sign_verify_bytes(signer: PgpEnvelopeSigner, key: pgpy.PGPKey) -> None:
    kref = {"kind": "pgpy_key", "priv": key}
    payload = b"hello"
    sigs = await signer.sign_bytes(kref, payload)
    assert await signer.verify_bytes(payload, sigs, opts={"pubkeys": [key]})


@pytest.mark.unit
@pytest.mark.asyncio
async def test_sign_verify_envelope_json(
    signer: PgpEnvelopeSigner, key: pgpy.PGPKey
) -> None:
    kref = {"kind": "pgpy_key", "priv": key}
    env = {"msg": "hi"}
    sigs = await signer.sign_envelope(kref, env, canon="json")
    assert await signer.verify_envelope(
        env, sigs, canon="json", opts={"pubkeys": [key]}
    )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_canon_cbor(signer: PgpEnvelopeSigner, key: pgpy.PGPKey) -> None:
    pytest.importorskip("cbor2")
    kref = {"kind": "pgpy_key", "priv": key}
    env = {"a": 1}
    sigs = await signer.sign_envelope(kref, env, canon="cbor")
    assert await signer.verify_envelope(
        env, sigs, canon="cbor", opts={"pubkeys": [key]}
    )


@pytest.mark.perf
def test_sign_perf(benchmark, signer: PgpEnvelopeSigner, key: pgpy.PGPKey) -> None:
    kref = {"kind": "pgpy_key", "priv": key}
    payload = b"x" * 1024

    def run() -> None:
        asyncio.run(signer.sign_bytes(kref, payload))

    benchmark(run)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_min_signers(signer: PgpEnvelopeSigner, key: pgpy.PGPKey) -> None:
    kref = {"kind": "pgpy_key", "priv": key}
    payload = b"data"
    sigs = await signer.sign_bytes(kref, payload)
    assert not await signer.verify_bytes(
        payload, sigs, require={"min_signers": 2}, opts={"pubkeys": [key]}
    )
