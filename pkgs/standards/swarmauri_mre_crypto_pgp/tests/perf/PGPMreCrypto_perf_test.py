import asyncio
import pgpy
import pytest
from swarmauri_mre_crypto_pgp import PGPMreCrypto


def _keypair():
    key = pgpy.PGPKey.new(pgpy.constants.PubKeyAlgorithm.RSAEncryptOrSign, 1024)
    uid = pgpy.PGPUID.new("Perf", email="perf@example.com")
    key.add_uid(
        uid,
        usage={pgpy.constants.KeyFlags.EncryptCommunications},
        hashes=[pgpy.constants.HashAlgorithm.SHA256],
        ciphers=[pgpy.constants.SymmetricKeyAlgorithm.AES256],
        compression=[pgpy.constants.CompressionAlgorithm.Uncompressed],
    )
    return {"kind": "pgpy_pub", "pub": key.pubkey}


@pytest.mark.perf
def test_encrypt_perf(benchmark):
    pub = _keypair()
    crypto = PGPMreCrypto()

    async def run():
        await crypto.encrypt_for_many([pub], b"bench")

    benchmark(lambda: asyncio.run(run()))
