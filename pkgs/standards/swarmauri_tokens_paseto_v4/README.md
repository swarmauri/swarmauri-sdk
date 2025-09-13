![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

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
