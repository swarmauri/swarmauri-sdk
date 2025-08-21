![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

# Swarmauri Signing JWS

Composite JWS signer/verifier supporting multiple algorithms and JWKS resolution.

Features:
- Compact and General JSON JWS
- HMAC, RSA, ECDSA, Ed25519, and optional secp256k1 algorithms
- RFC 7515 and RFC 7797 (unencoded payload) compliance

## Installation

```bash
pip install swarmauri_signing_jws
```

## Usage

```python
from swarmauri_signing_jws import JwsSignerVerifier

jws = JwsSignerVerifier()
```

## Entry Point

Registers `JwsSignerVerifier` under the `swarmauri.signings` entry point.
