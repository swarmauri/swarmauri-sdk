![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/master/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_cipher_ipsec/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_cipher_ipsec" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_cipher_ipsec/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_cipher_ipsec.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_cipher_ipsec/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_cipher_ipsec" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_cipher_ipsec/">
        <img src="https://img.shields.io/pypi/l/swarmauri_cipher_ipsec" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_cipher_ipsec/">
        <img src="https://img.shields.io/pypi/v/swarmauri_cipher_ipsec?label=swarmauri_cipher_ipsec&color=green" alt="PyPI - swarmauri_cipher_ipsec"/></a>
</p>

---

# Swarmauri Cipher Ipsec

IPsec / IKE AEAD, PRF, and DH defaults for tunnel policies.

## Installation

### pip

```bash
pip install swarmauri_cipher_ipsec
```

### Poetry

```bash
poetry add swarmauri_cipher_ipsec
```

### uv

To add the dependency to a `pyproject.toml` managed by `uv`:

```bash
uv add swarmauri_cipher_ipsec
```

Or install it into the active environment:

```bash
uv pip install swarmauri_cipher_ipsec
```

## Usage

```python
from swarmauri_cipher_ipsec import IpsecCipherSuite

suite = IpsecCipherSuite(name="demo-ipsec")

# Inspect the available operations and defaults
print(suite.features()["ops"].keys())

# Normalize an operation
descriptor = suite.normalize(op=list(suite.supports().keys())[0])
print(descriptor["alg"], descriptor["params"])
```

The suite returns normalized descriptors that include canonical algorithm names,
per-dialect mappings, and policy metadata so providers can focus on execution.

## Entry Point

The suite registers under the `swarmauri.cipher_suites` entry point as `IpsecCipherSuite`.

## Contributing

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.
