<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
</picture>

# Swarmauri Tokens TLS-Bound JWT

A mutual-TLS bound JWT token service per [RFC 8705](https://www.rfc-editor.org/rfc/rfc8705).
It derives the `x5t#S256` confirmation claim from the current client certificate
and verifies that presented certificates match the token binding.

Features:
- Automatic `cnf` claim insertion with the SHA-256 thumbprint of the client certificate
- Verification that rejects tokens when the live certificate is missing or mismatched

## Installation

```bash
pip install swarmauri_tokens_tlsboundjwt
```

## Usage

```python
from swarmauri_core.crypto.types import JWAAlg
from swarmauri_tokens_tlsboundjwt import TlsBoundJWTTokenService

svc = TlsBoundJWTTokenService(key_provider, client_cert_der_getter=my_cert_getter)
await svc.mint({"sub": "alice"}, alg=JWAAlg.HS256)
```

## Entry Point

The service registers under the `swarmauri.tokens` entry point as
`TlsBoundJWTTokenService`.
