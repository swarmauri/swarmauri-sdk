<!-- Dark OS/GitHub theme → show LIGHT PNG; Light → show DARK PNG -->
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="../../../assets/swarmauri_brand_frag_light.png">
  <source media="(prefers-color-scheme: light)" srcset="../../../assets/swarmauri_brand_frag_dark.png">
  <!-- Fallback below (see #2) -->
  <img alt="Project logo" src="../../../assets/swarmauri_brand_frag_dark.png" width="640">
</picture>


# Swarmauri Token Paseto V4

PASETO v4 token service implementing the `ITokenService` interface for
`v4.public` and `v4.local` operations using the `pyseto` library.

Features:
- Ed25519 signing for `v4.public`
- XChaCha20-Poly1305 encryption for `v4.local`
- Registered claim validation (RFC 7519)
- Optional CBOR canonicalization via the `cbor` extra

## Installation

```bash
pip install swarmauri_tokens_paseto_v4
```

## Usage

```python
from swarmauri_tokens_paseto_v4 import PasetoV4TokenService
```
