![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)


<p align="center">
    <a href="https://pypi.org/project/swarmauri_signing_jws/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_signing_jws" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_jws/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_jws.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_jws/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_signing_jws" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_jws/">
        <img src="https://img.shields.io/pypi/l/swarmauri_signing_jws" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_jws/">
        <img src="https://img.shields.io/pypi/v/swarmauri_signing_jws?label=swarmauri_signing_jws&color=green" alt="PyPI - swarmauri_signing_jws"/></a>
</p>

---

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
