![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

# Swarmauri File Key Provider

A file-backed key provider implementing the `KeyProviderBase` interface.
It manages symmetric and asymmetric keys on disk and exports public material via JWK/JWKS.

## Installation

```bash
pip install swarmauri_keyprovider_file
```

## Entry Point

The provider registers under the `swarmauri.key_providers` entry point as `FileKeyProvider`.
