![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

# Swarmauri Middleware JWKS Verifier

A middleware component providing JWT verification using a cached JWKS with TTL and LRU eviction.

Features:
- Supports RSA, EC, Ed25519, and HMAC keys from JWKS (RFC 7517)
- Thread-safe cache with TTL refresh and LRU eviction
- Optional issuer and algorithm whitelisting

## Installation

```bash
pip install swarmauri_middleware_jwksverifier
```

## Usage

```python
from swarmauri_middleware_jwksverifier import CachedJWKSVerifier

verifier = CachedJWKSVerifier(fetch=my_fetch_jwks)
claims = verifier.verify(token, algorithms_whitelist=["RS256"], audience="me")
```

## Entry Point

The middleware registers under the `swarmauri.middlewares` entry point as `CachedJWKSVerifier`.
