import asyncio
import base64
import json

import pytest

from swarmauri_crypto_jwe import JweCrypto


@pytest.mark.unit
@pytest.mark.test
def test_rfc7516_compact_structure() -> None:
    crypto = JweCrypto()
    key = {"k": b"0" * 32}
    jwe = asyncio.run(
        crypto.encrypt_compact(payload=b"hi", alg="dir", enc="A256GCM", key=key)
    )
    parts = jwe.split(".")
    assert len(parts) == 5
    header = json.loads(base64.urlsafe_b64decode(parts[0] + "=="))
    assert header["alg"] == "dir"
    assert header["enc"] == "A256GCM"
