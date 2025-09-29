![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/master/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_cipher_fips1403/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_cipher_fips1403" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_cipher_fips1403/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_cipher_fips1403.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_cipher_fips1403/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_cipher_fips1403" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_cipher_fips1403/">
        <img src="https://img.shields.io/pypi/l/swarmauri_cipher_fips1403" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_cipher_fips1403/">
        <img src="https://img.shields.io/pypi/v/swarmauri_cipher_fips1403?label=swarmauri_cipher_fips1403&color=green" alt="PyPI - swarmauri_cipher_fips1403"/></a>
</p>

---

# Swarmauri Cipher FIPS 140-3

Policy-enforcing cipher suite that restricts operations to NIST FIPS 140-3
validated algorithms and parameter settings.

## Features

- Enforces RSA minimum modulus sizes, approved elliptic curves, and SHA hashes
- Provides FIPS-aligned defaults for AES-GCM, RSA-OAEP, and RSA-PSS operations
- Shares structured policy metadata so calling services understand enforced
  constraints
- Can be swapped with the JWA or COSE suites for tenants that require
  FIPS-only cryptography

## Installation

### pip

```bash
pip install swarmauri_cipher_fips1403
```

### Poetry

```bash
poetry add swarmauri_cipher_fips1403
```

### uv

To add the dependency to a `pyproject.toml` managed by `uv`:

```bash
uv add swarmauri_cipher_fips1403
```

Or install it into the active environment:

```bash
uv pip install swarmauri_cipher_fips1403
```

## Usage

```python
from swarmauri_cipher_fips1403 import FipsCipherSuite

suite = FipsCipherSuite(name="fips-mode")

# Describe a compliant RSA-PSS signing request
descriptor = suite.normalize(op="sign", alg="PS256")
print(descriptor["params"]["saltBits"])   # -> 256 enforced default
print(descriptor["constraints"]["minKeyBits"])  # -> 2048 minimum RSA modulus
```

If an unsupported algorithm is requested, the suite raises `ValueError`
immediately, making it straightforward for upstream services to surface a
policy violation.

## Entry Point

The suite registers under the `swarmauri.cipher_suites` entry point as
`FipsCipherSuite`.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.
