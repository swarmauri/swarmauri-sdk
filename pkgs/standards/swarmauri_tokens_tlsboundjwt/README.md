![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

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
from swarmauri_tokens_tlsboundjwt import TlsBoundJWTTokenService

svc = TlsBoundJWTTokenService(key_provider, client_cert_der_getter=my_cert_getter)
await svc.mint({"sub": "alice"}, alg="HS256")
```

## Entry Point

The service registers under the `swarmauri.tokens` entry point as
`TlsBoundJWTTokenService`.
