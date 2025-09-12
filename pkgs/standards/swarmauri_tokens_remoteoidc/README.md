![Swarmauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tokens_remoteoidc/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tokens_remoteoidc" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tokens_remoteoidc/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tokens_remoteoidc.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tokens_remoteoidc/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tokens_remoteoidc" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tokens_remoteoidc/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tokens_remoteoidc" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tokens_remoteoidc/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tokens_remoteoidc?label=swarmauri_tokens_remoteoidc&color=green" alt="PyPI - swarmauri_tokens_remoteoidc"/></a>

</p>

---

# swarmauri_tokens_remoteoidc

Remote OIDC token verification service for Swarmauri.

This package provides a verification-only token service that retrieves
JSON Web Key Sets (JWKS) from a remote OpenID Connect (OIDC) issuer and
validates JWTs in accordance with RFC 7517 and RFC 7519.

## Features
- Remote OIDC discovery with JWKS caching.
- Audience and issuer validation.
- Optional extras for additional canonicalisation formats.

