![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_crypto_composite/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_crypto_composite" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_crypto_composite/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_crypto_composite.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_crypto_composite/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_crypto_composite" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_crypto_composite/">
        <img src="https://img.shields.io/pypi/l/swarmauri_crypto_composite" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_crypto_composite/">
        <img src="https://img.shields.io/pypi/v/swarmauri_crypto_composite?label=swarmauri_crypto_composite&color=green" alt="PyPI - swarmauri_crypto_composite"/></a>
</p>

---

## Swarmauri Crypto Composite

Algorithm-routing crypto provider delegating to child providers based on requested algorithms.

## Installation

```bash
pip install swarmauri_crypto_composite
```

## Usage

```python
from swarmauri_crypto_composite import CompositeCrypto

crypto = CompositeCrypto([...])  # pass in other ICrypto providers
```

## Entry point

The provider is registered under the `swarmauri.cryptos` entry-point as `CompositeCrypto`.
