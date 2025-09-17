![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)


<p align="center">
    <a href="https://pypi.org/project/swarmauri_middleware_jwksverifier/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_middleware_jwksverifier" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_jwksverifier/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_jwksverifier.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_middleware_jwksverifier/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_middleware_jwksverifier" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_middleware_jwksverifier/">
        <img src="https://img.shields.io/pypi/l/swarmauri_middleware_jwksverifier" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_middleware_jwksverifier/">
        <img src="https://img.shields.io/pypi/v/swarmauri_middleware_jwksverifier?label=swarmauri_middleware_jwksverifier&color=green" alt="PyPI - swarmauri_middleware_jwksverifier"/></a>
</p>

---

# Swarmauri Middleware JWKS Verifier

A middleware component providing JWT verification using a cached JWKS with TTL
and LRU eviction.

## Features

- Parses RSA, EC, Ed25519, and HMAC keys from JWKS documents (RFC 7517).
- Thread-safe cache with configurable TTL refresh and LRU eviction limits.
- Optional constructor guards for allowed algorithms and issuer values.
- Manual cache controls for forced refreshes, invalidation, and overrides.

## Installation

Install the package with your preferred Python packaging tool:

```bash
pip install swarmauri_middleware_jwksverifier
```

```bash
poetry add swarmauri_middleware_jwksverifier
```

```bash
uv pip install swarmauri_middleware_jwksverifier
```

## Quickstart

`CachedJWKSVerifier` expects a callable that returns a JWKS document. The fetch
callback is invoked whenever the cache expires (default `ttl_s=300` seconds) or
when a forced refresh is requested.

The verifier exposes a `verify` helper that performs signature validation and
standard PyJWT checks. Pass the algorithms you are willing to accept by
supplying the `algorithms_whitelist` parameter on every verification call. If
you do not provide an explicit `issuer`, the first value from
`allowed_issuers` (if configured during construction) is used.

```python
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
                "k": base64.urlsafe_b64encode(SECRET).rstrip(b"=").decode("ascii"),
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
```

### Cache management helpers

- `refresh(force: bool = False)` — trigger a JWKS refresh immediately when
  `force` is true or the cache has expired.
- `invalidate(kid: Optional[str] = None)` — drop either a specific key or the
  entire cache, including overrides.
- `inject_override_key(kid, key_obj)` / `inject_override_jwk(kid, jwk)` — add
  temporary key material that bypasses JWKS fetching when resolving by `kid`.
- `key_resolver()` — obtain a callable suitable for advanced PyJWT usage when
  integrating with other verification flows.

## Entry Point

The middleware registers under the `swarmauri.middlewares` entry point as
`CachedJWKSVerifier`.
