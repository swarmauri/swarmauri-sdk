![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/master/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_cipher_suite_fips203/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_cipher_suite_fips203" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_cipher_suite_fips203/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_cipher_suite_fips203.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_cipher_suite_fips203/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_cipher_suite_fips203" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_cipher_suite_fips203/">
        <img src="https://img.shields.io/pypi/l/swarmauri_cipher_suite_fips203" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_cipher_suite_fips203/">
        <img src="https://img.shields.io/pypi/v/swarmauri_cipher_suite_fips203?label=swarmauri_cipher_suite_fips203&color=green" alt="PyPI - swarmauri_cipher_suite_fips203"/></a>
</p>

---

# Swarmauri Cipher Suite FIPS 203

Cipher suite bindings for the post-quantum ML-KEM key encapsulation mechanisms
standardised in NIST FIPS 203.

## Features

- Enumerates the ML-KEM-512, ML-KEM-768, and ML-KEM-1024 parameter sets
- Describes NIST security level metadata for downstream policy enforcement
- Normalises wrap / unwrap requests with provider-oriented descriptors
- Ships entry-point metadata for seamless Swarmauri component discovery

## Installation

### pip

```bash
pip install swarmauri_cipher_suite_fips203
```

### Poetry

```bash
poetry add swarmauri_cipher_suite_fips203
```

### uv

To add the dependency to a `pyproject.toml` managed by `uv`:

```bash
uv add swarmauri_cipher_suite_fips203
```

Or install it into the active environment:

```bash
uv pip install swarmauri_cipher_suite_fips203
```

## Usage

```python
from swarmauri_cipher_suite_fips203 import Fips203CipherSuite

suite = Fips203CipherSuite(name="mlkem")

# Describe a ML-KEM-768 key encapsulation request
descriptor = suite.normalize(op="wrap", alg="ML-KEM-768")
print(descriptor["constraints"]["nistLevel"])  # -> 3
print(descriptor["mapped"]["provider"])       # -> ml-kem:ML-KEM-768
```

The suite raises `ValueError` if a non-ML-KEM algorithm is requested, allowing
callers to surface the policy violation immediately.

## Entry Point

The suite registers under the `swarmauri.cipher_suites` entry point as
`Fips203CipherSuite`.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.
