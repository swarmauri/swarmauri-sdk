import asyncio

import pytest

from swarmauri_core.crypto.types import JWAAlg
from swarmauri_crypto_jwe import JweCrypto


@pytest.mark.unit
@pytest.mark.test
def test_dir_encrypt_decrypt_unit() -> None:
    crypto = JweCrypto()
    key = {"k": b"0" * 32}
    message = b"unit-test"

    jwe = asyncio.run(
        crypto.encrypt_compact(
            payload=message, alg=JWAAlg.DIR, enc=JWAAlg.A256GCM, key=key
        )
    )
    res = asyncio.run(crypto.decrypt_compact(jwe, dir_key=key["k"]))
    assert res.plaintext == message
