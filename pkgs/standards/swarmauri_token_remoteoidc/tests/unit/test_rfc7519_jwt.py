import asyncio
import json
import time

from cryptography.hazmat.primitives.asymmetric import rsa
from jwt import algorithms
import jwt

from swarmauri_token_remoteoidc import RemoteOIDCTokenService


def _create_service(tmp_path):
    sk = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pk = sk.public_key()
    jwk = json.loads(algorithms.RSAAlgorithm.to_jwk(pk))
    jwk["kid"] = "kid1"
    jwk["use"] = "sig"
    jwks_path = tmp_path / "jwks.json"
    jwks_path.write_text(json.dumps({"keys": [jwk]}))
    service = RemoteOIDCTokenService(
        "https://example.com", jwks_url=f"file://{jwks_path}"
    )
    token = jwt.encode(
        {
            "iss": "https://example.com",
            "sub": "123",
            "aud": "test",
            "exp": int(time.time()) + 300,
            "iat": int(time.time()),
        },
        sk,
        algorithm="RS256",
        headers={"kid": "kid1"},
    )
    return service, token


def test_rfc7519_jwt_claims(tmp_path):
    service, token = _create_service(tmp_path)
    claims = asyncio.run(service.verify(token, audience="test"))
    assert claims["sub"] == "123"
