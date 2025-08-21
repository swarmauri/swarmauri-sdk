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

from swarmauri_mre_crypto_pgpseal import PGPSealMreCrypto


def _generate_key() -> PGPKey:
    key = PGPKey.new(PubKeyAlgorithm.RSAEncryptOrSign, 2048)
    uid = PGPUID.new("Perf", email="perf@example.com")
    key.add_uid(
        uid,
        usage={KeyFlags.EncryptCommunications},
        hashes=[HashAlgorithm.SHA256],
        ciphers=[SymmetricKeyAlgorithm.AES256],
        compression=[CompressionAlgorithm.ZLIB],
    )
    return key


@pytest.mark.perf
@pytest.mark.test
def test_encrypt_perf(benchmark):
    key = _generate_key()
    crypto = PGPSealMreCrypto()
    recipients = [{"kind": "pgpy_pub", "pub": key.pubkey}]
    pt = b"x" * 32

    def run():
        return asyncio.run(crypto.encrypt_for_many(recipients, pt))

    benchmark(run)
