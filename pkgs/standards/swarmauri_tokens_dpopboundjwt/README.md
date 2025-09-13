<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
</picture>

# Swarmauri Tokens DPoP Bound JWT

DPoP-bound JSON Web Token (JWT) service for Swarmauri implementing
[RFC 9449](https://www.rfc-editor.org/rfc/rfc9449) and JWK thumbprint
handling per [RFC 7638](https://www.rfc-editor.org/rfc/rfc7638).

Features:
- Mints and verifies DPoP-bound JWTs
- Computes JWK thumbprints for binding proofs
- Optional replay protection hook

## Installation

```bash
pip install swarmauri_tokens_dpopboundjwt
```

## Usage

```python
from swarmauri_tokens_dpopboundjwt import DPoPBoundJWTTokenService

service = DPoPBoundJWTTokenService(key_provider)
```

## Entry Point

The service registers under the `swarmauri.tokens` entry point as
`DPoPBoundJWTTokenService`.
