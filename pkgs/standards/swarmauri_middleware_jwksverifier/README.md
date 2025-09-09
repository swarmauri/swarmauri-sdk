<!-- Dark OS/GitHub theme → show LIGHT PNG; Light → show DARK PNG -->
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="../../../assets/swarmauri_brand_frag_light.png">
  <source media="(prefers-color-scheme: light)" srcset="../../../assets/swarmauri_brand_frag_dark.png">
  <!-- Fallback below (see #2) -->
  <img alt="Project logo" src="../../../assets/swarmauri_brand_frag_dark.png" width="640">
</picture>


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
