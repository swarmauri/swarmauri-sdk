<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
</picture>

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
from swarmauri_keyprovider_local import LocalKeyProvider

primary = LocalKeyProvider()
secondary = LocalKeyProvider()
provider = MirroredKeyProvider(primary, secondary)
```

## Entry Point

The provider registers under the `swarmauri.key_providers` entry point as
`MirroredKeyProvider`.

