import asyncio
import json

from cryptography.hazmat.primitives.asymmetric import rsa
from jwt import algorithms

from swarmauri_tokens_remoteoidc import RemoteOIDCTokenService


def test_rfc7517_jwks_usage(tmp_path):
    sk = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pk = sk.public_key()
    jwk = json.loads(algorithms.RSAAlgorithm.to_jwk(pk))
    jwk["kid"] = "kid1"
    jwks_path = tmp_path / "jwks.json"
    jwks_path.write_text(json.dumps({"keys": [jwk]}))
    service = RemoteOIDCTokenService("https://issuer", jwks_url=f"file://{jwks_path}")
    jwks = asyncio.run(service.jwks())
    assert jwks["keys"][0]["kid"] == "kid1"
