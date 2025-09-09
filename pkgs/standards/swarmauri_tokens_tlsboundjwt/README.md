<!-- Dark OS/GitHub theme → show LIGHT PNG; Light → show DARK PNG -->
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="../../../assets/swarmauri_brand_frag_light.png">
  <source media="(prefers-color-scheme: light)" srcset="../../../assets/swarmauri_brand_frag_dark.png">
  <!-- Fallback below (see #2) -->
  <img alt="Project logo" src="../../../assets/swarmauri_brand_frag_dark.png" width="640">
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
