import asyncio
import pytest

from swarmauri_signing_jws import JwsSignerVerifier


@pytest.mark.unit
def test_rfc7797_unencoded_payload() -> None:
    signer = JwsSignerVerifier()
    key = {"kind": "raw", "key": b"secret"}
    payload = "Hello world"
    token = asyncio.run(
        signer.sign_compact(
            payload=payload,
            alg="HS256",
            key=key,
            header_extra={"b64": False, "crit": ["b64"]},
        )
    )
    result = asyncio.run(signer.verify_compact(token, hmac_keys=[key]))
    assert result.payload.decode() == payload
    assert result.header["b64"] is False
