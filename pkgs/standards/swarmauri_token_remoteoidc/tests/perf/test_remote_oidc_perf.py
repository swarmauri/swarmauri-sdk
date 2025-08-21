import asyncio
import json
import time

from cryptography.hazmat.primitives.asymmetric import rsa
from jwt import algorithms
import jwt
import pytest

from swarmauri_token_remoteoidc import RemoteOIDCTokenService


@pytest.mark.perf
def test_verify_perf(tmp_path, benchmark):
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

    def _verify():
        asyncio.run(service.verify(token, audience="ok"))

    benchmark(_verify)
