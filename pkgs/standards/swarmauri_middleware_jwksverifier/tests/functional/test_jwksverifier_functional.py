import json
from typing import Dict

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa

from swarmauri_middleware_jwksverifier import CachedJWKSVerifier


def _pub_jwk(pk, kid: str) -> Dict[str, object]:
    jwk = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(pk.public_key()))
    jwk["kid"] = kid
    return jwk


def test_refresh_and_verify_functional() -> None:
    pk1 = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pk2 = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    current = {"keys": [_pub_jwk(pk1, "a")]}

    def fetch():
        return current

    v = CachedJWKSVerifier(fetch=fetch, ttl_s=0)
    t1 = jwt.encode({"iss": "me"}, pk1, algorithm="RS256", headers={"kid": "a"})
    assert v.verify(t1, algorithms_whitelist=["RS256"], issuer="me")["iss"] == "me"

    current["keys"] = [_pub_jwk(pk2, "b")]
    t2 = jwt.encode({"iss": "me"}, pk2, algorithm="RS256", headers={"kid": "b"})
    v.invalidate()
    assert v.verify(t2, algorithms_whitelist=["RS256"], issuer="me")["iss"] == "me"
