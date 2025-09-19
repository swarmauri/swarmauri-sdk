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

Composite JSON Web Signature (JWS) signer and verifier that orchestrates
multiple Swarmauri signing providers behind a single asynchronous API.

## Features

- Async helpers for both compact and general JSON JWS serialization
- Algorithm routing across HMAC (HS256/384/512), RSA (RS*/PS*), ECDSA
  (ES256/384/512), Ed25519 (EdDSA), and optional secp256k1 (ES256K when the
  `secp256k1` extra is installed)
- Works with direct key material, Swarmauri signer objects, or a JWKS resolver
  while returning the protected header and payload via `JwsResult`

## Installation

### pip

```bash
pip install swarmauri_signing_jws
```

### Poetry

```bash
poetry add swarmauri_signing_jws
```

### uv

To add the dependency to a `pyproject.toml` managed by `uv`:

```bash
uv add swarmauri_signing_jws
```

Or install it into the active environment:

```bash
uv pip install swarmauri_signing_jws
```

Optional extras:

- `secp256k1` enables ES256K support through `swarmauri_signing_secp256k1`

## Usage

```python
import asyncio
from swarmauri_signing_jws import JwsSignerVerifier


async def main() -> None:
    signer = JwsSignerVerifier()
    key = {"kind": "raw", "key": "0" * 32}

    compact = await signer.sign_compact(
        payload={"msg": "hi"},
        alg="HS256",
        key=key,
    )

    result = await signer.verify_compact(
        compact,
        hmac_keys=[key],
    )

    print(result.payload.decode("utf-8"))


if __name__ == "__main__":
    asyncio.run(main())
```

The public methods accept either raw strings or `JWAAlg` enum values for the
`alg` parameter. Compact verification returns a `JwsResult` dataclass containing
the parsed header and payload bytes so applications can safely forward or decode
the authenticated message.

## API highlights

- `sign_compact(...)` / `verify_compact(...)` wrap the standard compact
  serialization, including optional allowlists and JWKS resolvers.
- `sign_general_json(...)` / `verify_general_json(...)` operate on the general
  JSON serialization and support multi-signer verification with `min_signers`
  thresholds.
- Each algorithm family accepts dedicated key collections (`hmac_keys`,
  `rsa_pubkeys`, `ec_pubkeys`, `ed_pubkeys`, `k1_pubkeys`) or a `jwks_resolver`
  callback for dynamic key retrieval.

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

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.