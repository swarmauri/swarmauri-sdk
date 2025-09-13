![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

# Swarmauri Signing JWS

Composite JSON Web Signature (JWS) signer and verifier combining multiple
Swarmauri signing providers.

Features:
- Supports compact and general JWS serialization
- Routes algorithms to existing HMAC, RSA, ECDSA, Ed25519, and optional
  secp256k1 signers
- Optional CBOR canonicalization via `cbor2`

## Installation

```bash
pip install swarmauri_signing_jws
```

## Usage

```python
from swarmauri_signing_jws import JwsSignerVerifier

verifier = JwsSignerVerifier()
compact = await verifier.sign_compact(payload={"msg": "hi"}, alg="HS256", key={"kind": "raw", "key": "secret"})
result = await verifier.verify_compact(compact, hmac_keys=[{"kind": "raw", "key": "secret"}])
```

## Entry Point

The signer registers under the `swarmauri.signings` entry point as
`JwsSignerVerifier`.
