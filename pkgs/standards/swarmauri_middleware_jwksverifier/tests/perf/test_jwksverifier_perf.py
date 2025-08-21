import json

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
import pytest

from swarmauri_middleware_jwksverifier import CachedJWKSVerifier


def _fetch(pk):
    jwk = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(pk.public_key()))
    jwk["kid"] = "perf"
    return {"keys": [jwk]}


@pytest.mark.perf
def test_verify_perf(benchmark):
    pk = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    def fetch():
        return _fetch(pk)

    v = CachedJWKSVerifier(fetch=fetch)
    token = jwt.encode({"iss": "me"}, pk, algorithm="RS256", headers={"kid": "perf"})

    def _run():
        v.verify(token, algorithms_whitelist=["RS256"], issuer="me")

    benchmark(_run)
