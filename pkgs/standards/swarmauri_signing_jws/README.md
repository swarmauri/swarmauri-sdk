<!-- Dark OS/GitHub theme → show LIGHT PNG; Light → show DARK PNG -->
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="../../../assets/swarmauri_brand_frag_light.png">
  <source media="(prefers-color-scheme: light)" srcset="../../../assets/swarmauri_brand_frag_dark.png">
  <!-- Fallback below (see #2) -->
  <img alt="Project logo" src="../../../assets/swarmauri_brand_frag_dark.png" width="640">
</picture>


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
