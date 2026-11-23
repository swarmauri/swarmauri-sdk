import base64

import jwt

from swarmauri_middleware_jwksverifier import CachedJWKSVerifier

SECRET = b"super-secret-signing-key"


def fetch_jwks() -> dict[str, object]:
    return {
        "keys": [
            {
                "kty": "oct",
                "kid": "demo",
                "k": base64.urlsafe_b64encode(SECRET)
                .rstrip(b"=")
                .decode("ascii"),
                "alg": "HS256",
            }
        ]
    }


verifier = CachedJWKSVerifier(fetch=fetch_jwks, ttl_s=60)

token = jwt.encode(
    {"sub": "user-123", "aud": "example-service"},
    SECRET,
    algorithm="HS256",
    headers={"kid": "demo"},
)

claims = verifier.verify(
    token,
    algorithms_whitelist=["HS256"],
    audience="example-service",
)

print(claims["sub"])
