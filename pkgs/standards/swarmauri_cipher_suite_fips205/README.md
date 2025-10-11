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

SLH-DSA (SPHINCS+) signature suite aligned with NIST FIPS 205.

## Features

- Exposes all SHA2 and SHAKE based SLH-DSA parameter sets from the standard
- Provides security level metadata for downstream admission control
- Supplies provider-oriented descriptors for Swarmauri signing flows
- Publishes an entry point for automatic suite discovery and registration

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

suite = Fips205CipherSuite(name="slhdsa")

# Normalise a SLH-DSA-SHAKE-192s signing request
descriptor = suite.normalize(op="sign", alg="SLH-DSA-SHAKE-192s")
print(descriptor["constraints"]["nistLevel"])  # -> 3
print(descriptor["mapped"]["provider"])       # -> slh-dsa:SLH-DSA-SHAKE-192s
```

Requests for non-SLH-DSA algorithms raise `ValueError`, surfacing the policy
violation early.

## Entry Point

The suite registers under the `swarmauri.cipher_suites` entry point as
`Fips205CipherSuite`.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.
