![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/master/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_cipher_suite_mlkem/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_cipher_suite_mlkem" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_cipher_suite_mlkem/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_cipher_suite_mlkem.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_cipher_suite_mlkem/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_cipher_suite_mlkem" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_cipher_suite_mlkem/">
        <img src="https://img.shields.io/pypi/l/swarmauri_cipher_suite_mlkem" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_cipher_suite_mlkem/">
        <img src="https://img.shields.io/pypi/v/swarmauri_cipher_suite_mlkem?label=swarmauri_cipher_suite_mlkem&color=green" alt="PyPI - swarmauri_cipher_suite_mlkem"/></a>
</p>

---

# Swarmauri Cipher Suite ML-KEM

Cipher suite support for the NIST FIPS 203 ML-KEM family (Kyber512/768/1024)
with built-in translations for TLS groups, JOSE `alg` values, and provider
identifiers.

## Features

- Presents ML-KEM-512/768/1024 for wrap/unwrap and seal/unseal operations
- Maps friendly aliases (Kyber, ML-KEM, MLKEM) onto canonical suite tokens
- Supplies TLS group identifiers, JOSE algorithms, and provider handles
- Exposes ciphertext, key, and shared-secret sizing metadata per variant
- Ships with entry point registration for automatic discovery in Swarmauri

## Installation

### pip

```bash
pip install swarmauri_cipher_suite_mlkem
```

### Poetry

```bash
poetry add swarmauri_cipher_suite_mlkem
```

### uv

To add the dependency to a `pyproject.toml` managed by `uv`:

```bash
uv add swarmauri_cipher_suite_mlkem
```

Or install it into the active environment:

```bash
uv pip install swarmauri_cipher_suite_mlkem
```

## Usage

```python
from swarmauri_cipher_suite_mlkem import MlkemCipherSuite

suite = MlkemCipherSuite(name="default-mlkem")

# Normalize a sealing request using an alias for ML-KEM-512
descriptor = suite.normalize(op="seal", alg="ML-KEM-512")
print(descriptor["alg"])                 # -> "mlkem512"
print(descriptor["mapped"]["tls"]["iana"])   # -> 512 (decimal IANA identifier)
print(descriptor["params"]["ciphertextLen"])  # -> 768 bytes
```

The descriptor contains the canonical algorithm token, dialect-specific
translations, and merged parameter set. Providers can share the suite to reuse
consistent ML-KEM policy across services.

## Entry Point

The suite registers under the `swarmauri.cipher_suites` entry point as
`MlkemCipherSuite`.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.
