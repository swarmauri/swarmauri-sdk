![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/master/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_cipher_jwa/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_cipher_jwa" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_cipher_jwa/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_cipher_jwa.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_cipher_jwa/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_cipher_jwa" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_cipher_jwa/">
        <img src="https://img.shields.io/pypi/l/swarmauri_cipher_jwa" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_cipher_jwa/">
        <img src="https://img.shields.io/pypi/v/swarmauri_cipher_jwa?label=swarmauri_cipher_jwa&color=green" alt="PyPI - swarmauri_cipher_jwa"/></a>
</p>

---

# Swarmauri Cipher JWA

Normalization-centric cipher suite that maps JSON Web Algorithm (JWA) names
into provider-friendly descriptors for Swarmauri crypto and signing
implementations.

## Features

- Centralizes JWA algorithm allow-lists for signing, encryption, and key
  management operations
- Provides dialect translation helpers for COSE identifiers and provider
  metadata
- Supplies sensible defaults so crypto providers can delegate algorithm
  selection to the suite
- Enforces consistent tag lengths and parameter shapes for AES-GCM and RSA-PSS

## Installation

### pip

```bash
pip install swarmauri_cipher_jwa
```

### Poetry

```bash
poetry add swarmauri_cipher_jwa
```

### uv

To add the dependency to a `pyproject.toml` managed by `uv`:

```bash
uv add swarmauri_cipher_jwa
```

Or install it into the active environment:

```bash
uv pip install swarmauri_cipher_jwa
```

## Usage

```python
from swarmauri_cipher_jwa import JwaCipherSuite
from swarmauri_core.crypto.types import KeyRef, KeyType, KeyUse, ExportPolicy

# Construct a key reference representative of the caller's key inventory
key = KeyRef(
    kid="demo-rsa",
    version=1,
    type=KeyType.RSA,
    uses=(KeyUse.SIGN, KeyUse.VERIFY),
    export_policy=ExportPolicy.PUBLIC_ONLY,
)

suite = JwaCipherSuite(name="default-jwa")

# Resolve the provider-facing descriptor for a signing request
descriptor = suite.normalize(op="sign", alg="PS256", key=key)
print(descriptor["mapped"]["provider"])  # -> "PS256"
print(descriptor["params"]["saltBits"])   # -> 256 (derived default)
```

`normalize` returns a structured dictionary containing the canonical algorithm,
per-dialect aliases, policy constraints, and defaulted parameters. Crypto and
signing providers consume this descriptor to select the correct primitives
without re-implementing JWA policy logic.

## Entry Point

The suite registers under the `swarmauri.cipher_suites` entry point as
`JwaCipherSuite`.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.
