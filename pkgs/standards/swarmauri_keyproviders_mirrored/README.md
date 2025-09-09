<!-- Dark OS/GitHub theme → show LIGHT PNG; Light → show DARK PNG -->
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="../../../assets/swarmauri_brand_frag_light.png">
  <source media="(prefers-color-scheme: light)" srcset="../../../assets/swarmauri_brand_frag_dark.png">
  <!-- Fallback below (see #2) -->
  <img alt="Project logo" src="../../../assets/swarmauri_brand_frag_dark.png" width="640">
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

