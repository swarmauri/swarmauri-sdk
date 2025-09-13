![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

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
