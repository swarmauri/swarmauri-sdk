![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)


<p align="center">
    <a href="https://pypi.org/project/swarmauri_signing_ed25519/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_signing_ed25519" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_ed25519/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_ed25519.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_ed25519/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_signing_ed25519" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_ed25519/">
        <img src="https://img.shields.io/pypi/l/swarmauri_signing_ed25519" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_ed25519/">
        <img src="https://img.shields.io/pypi/v/swarmauri_signing_ed25519?label=swarmauri_signing_ed25519&color=green" alt="PyPI - swarmauri_signing_ed25519"/></a>
</p>

---

# Swarmauri Signing Ed25519

`swarmauri_signing_ed25519` provides an Ed25519 implementation of the
`ISigning` interface for creating detached signatures over byte payloads and
canonicalized envelopes.

## Features

- Deterministic JSON canonicalization is always available, ensuring stable
  digests for dictionary-based envelopes.
- Optional CBOR canonicalization can be enabled with the `[cbor]` extra to
  install the `cbor2` dependency.
- Detached signatures are produced with `cryptography`'s Ed25519 primitives and
  returned as sequences so multi-signature workflows remain possible.
- Verification accepts multiple public keys via `opts["pubkeys"]` and honours
  `require={"min_signers": N}` for quorum checks.
- Ed25519 private keys can be supplied either as cryptography objects or raw
  seed bytes using the `KeyRef` helper structure from `swarmauri_core`.

## Installation

### pip

```bash
pip install swarmauri_signing_ed25519
```

### Poetry

```bash
poetry add swarmauri_signing_ed25519
```

### uv

```bash
uv add swarmauri_signing_ed25519
```

Install with the `[cbor]` extra when CBOR canonicalization is required:

```bash
pip install "swarmauri_signing_ed25519[cbor]"
poetry add swarmauri_signing_ed25519[cbor]
uv add swarmauri_signing_ed25519[cbor]
```

## Usage

The package exposes a single entry point, `Ed25519EnvelopeSigner`, implementing
`ISigning`. The signer reports JSON (and optionally CBOR) support via
`supports()`, canonicalizes envelopes through `canonicalize_envelope`, and
produces detached signatures using `sign_bytes`/`sign_envelope`. Verification
expects the relevant public keys to be supplied using `opts["pubkeys"]`.

### Key references

`Ed25519EnvelopeSigner` accepts Ed25519 private keys using `KeyRef` values. The
two supported forms are:

- `{"kind": "cryptography_obj", "obj": Ed25519PrivateKey}` for in-memory
  cryptography objects.
- `{"kind": "raw_ed25519_sk", "bytes": seed}` where `seed` is the 32-byte
  private key seed (or the 64-byte expanded secret key).

## Example

The example below signs a JSON envelope and verifies the detached signature with
the generated public key.

<!-- example-start -->
```python
import asyncio
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from swarmauri_signing_ed25519 import Ed25519EnvelopeSigner


async def main() -> bool:
    signer = Ed25519EnvelopeSigner()
    private_key = Ed25519PrivateKey.generate()
    key_ref = {"kind": "cryptography_obj", "obj": private_key}

    envelope = {"subject": "alice", "scope": ["inbox:read"]}
    signatures = await signer.sign_envelope(key_ref, envelope)

    public_key = private_key.public_key()
    verified = await signer.verify_envelope(
        envelope,
        signatures,
        opts={"pubkeys": [public_key]},
    )
    return verified


verified = asyncio.run(main())
print(f"Signature verified? {verified}")
```
<!-- example-end -->

## Entry Point

The signer registers under the `swarmauri.signings` entry point as
`Ed25519EnvelopeSigner`.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.