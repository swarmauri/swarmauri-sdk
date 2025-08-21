# swarmauri_tokens_remoteoidc

Remote OIDC token verification service for Swarmauri.

This package provides a verification-only token service that retrieves
JSON Web Key Sets (JWKS) from a remote OpenID Connect (OIDC) issuer and
validates JWTs in accordance with RFC 7517 and RFC 7519.

## Features
- Remote OIDC discovery with JWKS caching.
- Audience and issuer validation.
- Optional extras for additional canonicalisation formats.

