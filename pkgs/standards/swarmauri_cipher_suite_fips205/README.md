![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/master/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_cipher_suite_fips205/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_cipher_suite_fips205" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_cipher_suite_fips205/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_cipher_suite_fips205.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_cipher_suite_fips205/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_cipher_suite_fips205" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_cipher_suite_fips205/">
        <img src="https://img.shields.io/pypi/l/swarmauri_cipher_suite_fips205" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_cipher_suite_fips205/">
        <img src="https://img.shields.io/pypi/v/swarmauri_cipher_suite_fips205?label=swarmauri_cipher_suite_fips205&color=green" alt="PyPI - swarmauri_cipher_suite_fips205"/></a>
</p>

---

# Swarmauri Cipher Suite FIPS 205

FIPS 205 introduces the stateless hash-based signature (SLH-DSA) family as
part of NIST's post-quantum cryptography transition. This package exposes a
policy-driven cipher suite that restricts signing requests to the SLH-DSA
parameter sets standardized in FIPS 205.

## Features

- Declares the complete FIPS 205 SLH-DSA algorithm menu with security
  categories and signature sizes
- Normalizes signing requests with consistent hash, variant, and
  signature-length metadata
- Shares structured policy information so upstream services can negotiate
  post-quantum signature support without bespoke configuration
- Provides a drop-in cipher suite implementation compatible with other
  Swarmauri policy components

## Installation

### pip

```bash
pip install swarmauri_cipher_suite_fips205
```

### Poetry

```bash
poetry add swarmauri_cipher_suite_fips205
```

### uv

To add the dependency to a `pyproject.toml` managed by `uv`:

```bash
uv add swarmauri_cipher_suite_fips205
```

Or install it into the active environment:

```bash
uv pip install swarmauri_cipher_suite_fips205
```

## Usage

```python
from swarmauri_cipher_suite_fips205 import Fips205CipherSuite

suite = Fips205CipherSuite(name="pq-signing")

# Describe a compliant SLH-DSA signing request
descriptor = suite.normalize(op="sign", alg="SLH-DSA-SHA2-192s")
print(descriptor["params"]["hash"])  # -> "SHA2-256"
print(descriptor["constraints"]["securityCategory"])  # -> 3 security strength
```

The suite raises `ValueError` if a non-FIPS 205 algorithm is requested,
allowing upstream systems to surface policy violations early in a workflow.

## Entry Point

The suite registers under the `swarmauri.cipher_suites` entry point as
`Fips205CipherSuite`.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.
