![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

# Swarmauri Mirrored Key Provider

A failover key provider that mirrors keys to a secondary provider for redundancy.
Supports full and public-only replication with optional extras for canonical
representations.

Features:
- Mirror new keys to a secondary provider
- Failover reads when the primary provider is unavailable
- JWKS union merging as described in RFC 7517
- Optional extras for JSON and CBOR canonicalization

## Installation

```bash
pip install swarmauri_keyproviders_mirrored
```

## Usage

```python
from swarmauri_keyproviders_mirrored import MirroredKeyProvider
from swarmauri_keyproviders import LocalKeyProvider

primary = LocalKeyProvider()
secondary = LocalKeyProvider()
provider = MirroredKeyProvider(primary, secondary)
```

## Entry Point

The provider registers under the `swarmauri.key_providers` entry point as
`MirroredKeyProvider`.

