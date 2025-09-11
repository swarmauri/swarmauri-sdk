![Swarmauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

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
