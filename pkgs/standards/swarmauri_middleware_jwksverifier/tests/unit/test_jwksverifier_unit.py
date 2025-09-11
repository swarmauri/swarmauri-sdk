import json
from typing import Dict

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa

from swarmauri_middleware_jwksverifier import CachedJWKSVerifier


def _make_fetcher(pk) -> Dict[str, object]:
    jwk = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(pk.public_key()))
    jwk["kid"] = "unit"
    return {"keys": [jwk]}


def test_verify_rsa_unit() -> None:
    pk = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    def fetch() -> Dict[str, object]:
        return _make_fetcher(pk)

    v = CachedJWKSVerifier(fetch=fetch)
    token = jwt.encode({"iss": "me"}, pk, algorithm="RS256", headers={"kid": "unit"})
    claims = v.verify(token, algorithms_whitelist=["RS256"], issuer="me")
    assert claims["iss"] == "me"
