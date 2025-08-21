import json
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
import jwt

from swarmauri_middleware_jwksverifier import CachedJWKSVerifier


def _jwks(pk):
    jwk = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(pk.public_key()))
    jwk["kid"] = "alg"
    return {"keys": [jwk]}


def test_alg_whitelist_rfc7515() -> None:
    pk = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    token = jwt.encode({"iss": "me"}, pk, algorithm="RS256", headers={"kid": "alg"})

    def fetch():
        return _jwks(pk)

    v = CachedJWKSVerifier(fetch=fetch, allowed_algs=["HS256"])
    with pytest.raises(jwt.InvalidAlgorithmError):
        v.verify(token, algorithms_whitelist=["RS256"], issuer="me")
