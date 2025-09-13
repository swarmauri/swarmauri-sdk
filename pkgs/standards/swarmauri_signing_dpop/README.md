![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_signing_dpop/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_signing_dpop" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_dpop/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_dpop.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_dpop/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_signing_dpop" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_dpop/">
        <img src="https://img.shields.io/pypi/l/swarmauri_signing_dpop" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_dpop/">
        <img src="https://img.shields.io/pypi/v/swarmauri_signing_dpop?label=swarmauri_signing_dpop&color=green" alt="PyPI - swarmauri_signing_dpop"/></a>
</p>

# Swarmauri Signing DPoP

DPoP proof signer/verifier implementing RFC 9449 for proof-of-possession over HTTP requests.

Features:
- Creates and validates `dpop+jwt` proofs with embedded JWK
- Supports `ES256`, `RS256`, and `EdDSA`
- Optional access-token hash binding (`ath`) and replay protection hooks

## Installation

```bash
pip install swarmauri_signing_dpop
```

## Usage

```python
import asyncio
from swarmauri_signing_dpop import DpopSigner

async def main() -> None:
    signer = DpopSigner()
    key = {"kind": "pem", "priv": PRIV_PEM_BYTES, "alg": "EdDSA"}
    sigs = await signer.sign_bytes(
        key,
        b"",
        opts={"htm": "GET", "htu": "https://api.example/x"},
    )
    ok = await signer.verify_bytes(
        b"",
        sigs,
        require={"htm": "GET", "htu": "https://api.example/x"},
    )
    assert ok

asyncio.run(main())
```

## Entry Point

The signer registers under the `swarmauri.signings` entry point as `DpopSigner`.
