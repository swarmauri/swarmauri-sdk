![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

# Swarmauri Key Providers

Collection of key provider implementations for the Swarmauri SDK.  These
providers implement the `IKeyProvider` interface for managing symmetric and
asymmetric keys and exporting public material via JWK/JWKS.
The `SshKeyProvider` covers algorithms defined in RFC 7517 (JWK) and
RFC 8037 (OKP/Ed25519) with accompanying compliance tests.

## Installation

```bash
pip install swarmauri_keyproviders
```

## Testing

Unit, functional, performance and RFC compliance tests are provided. Run
them with:

```bash
uv run --package swarmauri_keyproviders --directory standards/swarmauri_keyproviders pytest
```
