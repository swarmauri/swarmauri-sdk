import asyncio

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


@pytest.mark.perf
@pytest.mark.test
def test_sign_verify_perf(benchmark):
    signer = PgpEnvelopeSigner()
    key = asyncio.run(_generate_key())
    key_ref = {"kind": "pgpy_key", "priv": key}
    payload = b"performance"

    async def _run():
        sigs = await signer.sign_bytes(key_ref, payload)
        return await signer.verify_bytes(payload, sigs, opts={"pubkeys": [key.pubkey]})

    result = benchmark(lambda: asyncio.run(_run()))
    assert result
