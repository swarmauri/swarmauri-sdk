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
