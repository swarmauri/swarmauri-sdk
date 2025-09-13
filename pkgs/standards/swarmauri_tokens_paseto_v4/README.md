<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
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
