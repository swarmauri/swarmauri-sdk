import asyncio
import json
import time

from cryptography.hazmat.primitives.asymmetric import rsa
from jwt import algorithms
import jwt
import pytest

from swarmauri_token_remoteoidc import RemoteOIDCTokenService


def test_verify_audience_functional(tmp_path):
    sk = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pk = sk.public_key()
    jwk = json.loads(algorithms.RSAAlgorithm.to_jwk(pk))
    jwk["kid"] = "kid1"
    jwks_path = tmp_path / "jwks.json"
    jwks_path.write_text(json.dumps({"keys": [jwk]}))
    service = RemoteOIDCTokenService("https://issuer", jwks_url=f"file://{jwks_path}")
    token = jwt.encode(
        {
            "iss": "https://issuer",
            "sub": "abc",
            "aud": "ok",
            "exp": int(time.time()) + 300,
            "iat": int(time.time()),
        },
        sk,
        algorithm="RS256",
        headers={"kid": "kid1"},
    )
    claims = asyncio.run(service.verify(token, audience="ok"))
    assert claims["sub"] == "abc"
    with pytest.raises(Exception):
        asyncio.run(service.verify(token, audience="other"))
