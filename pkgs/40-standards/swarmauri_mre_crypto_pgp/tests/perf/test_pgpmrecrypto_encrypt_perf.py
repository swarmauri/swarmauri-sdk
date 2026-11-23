import asyncio

import pytest
from pgpy import PGPKey, PGPUID
from pgpy.constants import (
    CompressionAlgorithm,
    HashAlgorithm,
    KeyFlags,
    PubKeyAlgorithm,
    SymmetricKeyAlgorithm,
)

from swarmauri_mre_crypto_pgp import PGPMreCrypto


def gen_key() -> PGPKey:
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
def test_encrypt_open_perf_pgpmrecrypto(benchmark):
    crypto = PGPMreCrypto()
    key = gen_key()
    pub_ref = {"kind": "pgpy_pub", "pub": key.pubkey}
    priv_ref = {"kind": "pgpy_priv", "priv": key}
    pt = b"performance"

    async def run():
        env = await crypto.encrypt_for_many([pub_ref], pt)
        return await crypto.open_for(priv_ref, env)

    result = benchmark(lambda: asyncio.run(run()))
    assert result == pt
