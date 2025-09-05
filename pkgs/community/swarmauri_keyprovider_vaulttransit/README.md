![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_keyprovider_vaulttransit/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_keyprovider_vaulttransit" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_keyprovider_vaulttransit/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_keyprovider_vaulttransit.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_vaulttransit/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_keyprovider_vaulttransit" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_vaulttransit/">
        <img src="https://img.shields.io/pypi/l/swarmauri_keyprovider_vaulttransit" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_vaulttransit/">
        <img src="https://img.shields.io/pypi/v/swarmauri_keyprovider_vaulttransit?label=swarmauri_keyprovider_vaulttransit&color=green" alt="PyPI - swarmauri_keyprovider_vaulttransit"/></a>
</p>

---

# Swarmauri Vault Transit Key Provider

A HashiCorp Vault Transit engine backed implementation of the Swarmauri key provider interface.

## Installation

```bash
pip install swarmauri_keyprovider_vaulttransit
```

## Usage

```python
from swarmauri.key_providers.VaultTransitKeyProvider import VaultTransitKeyProvider

provider = VaultTransitKeyProvider(url="http://localhost:8200", token="root")
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md).
