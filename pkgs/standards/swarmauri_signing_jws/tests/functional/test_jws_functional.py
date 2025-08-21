import asyncio
import base64
import json
import pytest

from swarmauri_signing_jws import JwsSignerVerifier


def _b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


@pytest.mark.test
def test_jwks_resolver_flow() -> None:
    signer = JwsSignerVerifier()
    key = {"kind": "raw", "key": b"secret"}
    payload = {"msg": "hi"}
    token = asyncio.run(
        signer.sign_compact(payload=payload, alg="HS256", key=key, kid="kid1")
    )

    def resolver(kid: str | None, alg: str) -> dict[str, str]:
        assert kid == "kid1"
        assert alg == "HS256"
        return {"kty": "oct", "k": _b64u(b"secret")}

    result = asyncio.run(signer.verify_compact(token, jwks_resolver=resolver))
    assert json.loads(result.payload) == payload
    assert result.header["kid"] == "kid1"
