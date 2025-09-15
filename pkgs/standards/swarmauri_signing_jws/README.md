![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)


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
compact = await verifier.sign_compact(
    payload={"msg": "hi"},
    alg="HS256",
    key={"kind": "raw", "key": "0" * 32},
)
result = await verifier.verify_compact(
    compact,
    hmac_keys=[{"kind": "raw", "key": "0" * 32}],
)
```

## HMAC key requirements

All HMAC-based operations **require a secret of at least 32 bytes (256 bits)**.  
Shorter keys are rejected to avoid truncation mistakes and to keep forgery
probabilities negligible even after many verification attempts.  

Rationale:

- Forgery success scales with tag length; a 256-bit tag keeps the chance
  negligible even after many tries ([NIST SP 800‑107 Rev.1](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-107r1.pdf)).
- [RFC 7518](https://datatracker.ietf.org/doc/html/rfc7518) already mandates
  HS256 keys ≥ 256 bits; using the full HMAC-SHA-256 output avoids
  inadvertent strength reduction.
- A full 32-byte tag preserves ≈128-bit security even under generic quantum
  search speedups ([NIST IR 8547](https://nvlpubs.nist.gov/nistpubs/ir/2024/NIST.IR.8547.ipd.pdf)).
- Fixed-length tags simplify constant-time verification and prevent
  configuration mismatches.

## Entry Point

The signer registers under the `swarmauri.signings` entry point as
`JwsSignerVerifier`.
