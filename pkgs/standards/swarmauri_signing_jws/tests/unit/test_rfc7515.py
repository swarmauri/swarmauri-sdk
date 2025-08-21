import asyncio
import json
import pytest

from swarmauri_signing_jws import JwsSignerVerifier


@pytest.mark.unit
def test_rfc7515_hs256_roundtrip() -> None:
    signer = JwsSignerVerifier()
    key = {"kind": "raw", "key": b"secret"}
    payload = {"iss": "joe", "exp": 1300819380, "http://example.com/is_root": True}
    token = asyncio.run(
        signer.sign_compact(
            payload=payload, alg="HS256", key=key, header_extra={"typ": "JWT"}
        )
    )
    result = asyncio.run(signer.verify_compact(token, hmac_keys=[key]))
    assert json.loads(result.payload) == payload
    assert result.header["typ"] == "JWT"
