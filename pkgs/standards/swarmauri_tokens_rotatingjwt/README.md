![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tokens_rotatingjwt/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tokens_rotatingjwt" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tokens_rotatingjwt/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tokens_rotatingjwt.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tokens_rotatingjwt/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tokens_rotatingjwt" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tokens_rotatingjwt/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tokens_rotatingjwt" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tokens_rotatingjwt/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tokens_rotatingjwt?label=swarmauri_tokens_rotatingjwt&color=green" alt="PyPI - swarmauri_tokens_rotatingjwt"/></a>

</p>

---

# swarmauri_tokens_rotatingjwt

Rotating JWT token service plugin for Swarmauri.

This package provides a token issuer/verifier that automatically rotates its
signing key.  It exposes a `RotatingJWTTokenService` implementing
`ITokenService` and conforms to RFC 7515, 7517, 7518 and 7519.

## Features

- Supports RS256, PS256, ES256, EdDSA and HS256 algorithms.
- Automatic key rotation based on time or token count.
- JWKS publication retaining previous key versions.

## Installation

```bash
uv add swarmauri_tokens_rotatingjwt
```

Optional extras are available for specific signing canons:

```bash
uv add swarmauri_tokens_rotatingjwt[rsa]
uv add swarmauri_tokens_rotatingjwt[ecdsa]
uv add swarmauri_tokens_rotatingjwt[eddsa]
uv add swarmauri_tokens_rotatingjwt[hmac]
```

## Usage

```python
from swarmauri_tokens_rotatingjwt import RotatingJWTTokenService
from swarmauri_keyprovider_inmemory import InMemoryKeyProvider
from swarmauri_core.crypto.types import JWAAlg

kp = InMemoryKeyProvider()
service = RotatingJWTTokenService(kp, alg=JWAAlg.RS256)

token = await service.mint({"sub": "alice"}, alg=JWAAlg.RS256)
claims = await service.verify(token)
jwks = await service.jwks()
```

The service handles key rotation based on time or token volume and exposes a
JWKS endpoint that includes previous keys so existing tokens remain valid.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.