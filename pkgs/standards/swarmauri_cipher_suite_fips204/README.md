![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/master/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_cipher_suite_fips204/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_cipher_suite_fips204" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_cipher_suite_fips204/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_cipher_suite_fips204.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_cipher_suite_fips204/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_cipher_suite_fips204" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_cipher_suite_fips204/">
        <img src="https://img.shields.io/pypi/l/swarmauri_cipher_suite_fips204" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_cipher_suite_fips204/">
        <img src="https://img.shields.io/pypi/v/swarmauri_cipher_suite_fips204?label=swarmauri_cipher_suite_fips204&color=green" alt="PyPI - swarmauri_cipher_suite_fips204"/></a>
</p>

---

# Swarmauri Cipher Suite FIPS 204

A FIPS 204 (ML-KEM) compliant cipher suite that limits key establishment to the
three parameter sets standardized by NIST for post-quantum hybrid deployments.

## Features

- Restricts the algorithm surface to ML-KEM-512, ML-KEM-768, and ML-KEM-1024 as
  defined by FIPS 204
- Exposes the NIST security level, ciphertext size, and shared-secret length for
  every allowed KEM parameter set
- Provides structured policy metadata that callers can use to negotiate
  FIPS-aligned post-quantum key establishment flows
- Shares defaults that prefer ML-KEM-768 for balanced performance and security

## Installation

### pip

```bash
pip install swarmauri_cipher_suite_fips204
```

### Poetry

```bash
poetry add swarmauri_cipher_suite_fips204
```

### uv

To add the dependency to a `pyproject.toml` managed by `uv`:

```bash
uv add swarmauri_cipher_suite_fips204
```

Or install it into the active environment:

```bash
uv pip install swarmauri_cipher_suite_fips204
```

## Usage

```python
from swarmauri_cipher_suite_fips204 import Fips204CipherSuite

suite = Fips204CipherSuite(name="fips-204")

# Normalize a default encapsulation request
descriptor = suite.normalize(op="wrap")
print(descriptor["alg"])  # -> ML-KEM-768
print(descriptor["params"]["securityLevel"])  # -> 3 (NIST level)
print(descriptor["constraints"]["ciphertextBytes"])  # -> 1088 bytes
```

When a caller requests an algorithm that is outside of the FIPS 204 surface the
suite immediately raises `ValueError`, allowing upstream systems to surface a
clear policy violation.

## Entry Point

The suite registers under the `swarmauri.cipher_suites` entry point as
`Fips204CipherSuite`.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.
