![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)


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
