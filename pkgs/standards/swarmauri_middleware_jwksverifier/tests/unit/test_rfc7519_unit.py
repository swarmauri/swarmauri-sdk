import json
from typing import Dict

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
import pytest

from swarmauri_middleware_jwksverifier import CachedJWKSVerifier


def _jwks(pk) -> Dict[str, object]:
    jwk = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(pk.public_key()))
    jwk["kid"] = "claims"
    return {"keys": [jwk]}


def test_issuer_and_audience_rfc7519() -> None:
    pk = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    token = jwt.encode(
        {"iss": "me", "aud": "you"}, pk, algorithm="RS256", headers={"kid": "claims"}
    )

    def fetch():
        return _jwks(pk)

    v = CachedJWKSVerifier(fetch=fetch, allowed_issuers=["me"])
    claims = v.verify(token, algorithms_whitelist=["RS256"], audience="you")
    assert claims["aud"] == "you"
    with pytest.raises(jwt.InvalidAudienceError):
        v.verify(token, algorithms_whitelist=["RS256"], audience="them")
