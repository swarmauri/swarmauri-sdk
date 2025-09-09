<!-- Dark OS/GitHub theme → show LIGHT PNG; Light → show DARK PNG -->
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="../../../assets/swarmauri_brand_frag_light.png">
  <source media="(prefers-color-scheme: light)" srcset="../../../assets/swarmauri_brand_frag_dark.png">
  <!-- Fallback below (see #2) -->
  <img alt="Project logo" src="../../../assets/swarmauri_brand_frag_dark.png" width="640">
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
