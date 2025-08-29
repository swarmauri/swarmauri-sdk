import asyncio
import base64
import json

import pytest

from swarmauri_core.crypto.types import JWAAlg
from swarmauri_crypto_jwe import JweCrypto


@pytest.mark.unit
@pytest.mark.test
def test_rfc7516_compact_structure() -> None:
    crypto = JweCrypto()
    key = {"k": b"0" * 32}
    jwe = asyncio.run(
        crypto.encrypt_compact(
            payload=b"hi", alg=JWAAlg.DIR, enc=JWAAlg.A256GCM, key=key
        )
    )
    parts = jwe.split(".")
    assert len(parts) == 5
    header = json.loads(base64.urlsafe_b64decode(parts[0] + "=="))
    assert header["alg"] == JWAAlg.DIR.value
    assert header["enc"] == JWAAlg.A256GCM.value
