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

ML-DSA (Dilithium) signature suite aligned with the requirements of NIST
FIPS 204.

## Features

- Supports ML-DSA-44, ML-DSA-65, and ML-DSA-87 parameter sets
- Provides NIST security level metadata for policy-aware services
- Normalises post-quantum signing requests using provider dialect mappings
- Integrates with Swarmauri discovery via the `swarmauri.cipher_suites` entry
  point

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

suite = Fips204CipherSuite(name="mldsa")

# Prepare a ML-DSA-65 signing descriptor
descriptor = suite.normalize(op="sign", alg="ML-DSA-65")
print(descriptor["constraints"]["nistLevel"])  # -> 3
print(descriptor["mapped"]["provider"])       # -> ml-dsa:ML-DSA-65
```

Unsupported algorithms raise `ValueError`, signalling the policy violation to
callers.

## Entry Point

The suite registers under the `swarmauri.cipher_suites` entry point as
`Fips204CipherSuite`.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.
