![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/master/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_cipher_suite_cose/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_cipher_suite_cose" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_cipher_suite_cose/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_cipher_suite_cose.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_cipher_suite_cose/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_cipher_suite_cose" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_cipher_suite_cose/">
        <img src="https://img.shields.io/pypi/l/swarmauri_cipher_suite_cose" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_cipher_suite_cose/">
        <img src="https://img.shields.io/pypi/v/swarmauri_cipher_suite_cose?label=swarmauri_cipher_suite_cose&color=green" alt="PyPI - swarmauri_cipher_suite_cose"/></a>
</p>

---

# Swarmauri Cipher COSE

Cipher suite that understands CBOR Object Signing and Encryption (COSE)
algorithm identifiers and maps them into Swarmauri crypto provider descriptors.

## Features

- Accepts both integer and string COSE algorithm identifiers while normalizing
  to canonical string tokens
- Supplies JWA aliases so cross-protocol code can align crypto operations
- Provides default AEAD tag sizing and metadata for providers that expect it
- Designed to be injected into crypto or signing providers for algorithm policy
  reuse

## Installation

### pip

```bash
pip install swarmauri_cipher_suite_cose
```

### Poetry

```bash
poetry add swarmauri_cipher_suite_cose
```

### uv

To add the dependency to a `pyproject.toml` managed by `uv`:

```bash
uv add swarmauri_cipher_suite_cose
```

Or install it into the active environment:

```bash
uv pip install swarmauri_cipher_suite_cose
```

## Usage

```python
from swarmauri_cipher_suite_cose import CoseCipherSuite

suite = CoseCipherSuite(name="default-cose")

# Normalize a COSE signing request using the integer identifier for EdDSA
descriptor = suite.normalize(op="sign", alg=-8)
print(descriptor["alg"])              # -> "-8"
print(descriptor["mapped"]["provider"])  # -> "-8"
print(descriptor["params"]["tagBits"])   # -> 128 for COSE AEAD defaults
```

The resulting descriptor captures the operation, canonical algorithm token,
provider mapping, and normalized parameter set. Crypto providers can share the
suite to avoid re-implementing COSE policy logic across code paths.

## Entry Point

The suite registers under the `swarmauri.cipher_suites` entry point as
`CoseCipherSuite`.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.
