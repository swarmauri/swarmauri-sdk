<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
</picture>

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

A HashiCorp Vault Transit engine backed implementation of the Swarmauri key
provider interface. It allows Swarmauri deployments to manage cryptographic
keys using Vault's Transit secret engine.

## Features

- Create and rotate symmetric or asymmetric keys
- Export public keys as JWK or JWKS documents
- Generate random bytes using Vault's RNG
- Derive keys with HKDF

## Prerequisites

- [HashiCorp Vault](https://www.vaultproject.io/) with the Transit engine
  enabled
- A Vault token with access to the desired mount point
- Optional: the [`hvac`](https://pypi.org/project/hvac/) client library

## Installation

```bash
pip install swarmauri_keyprovider_vaulttransit
```

## Usage

```python
from swarmauri_keyprovider_vaulttransit import VaultTransitKeyProvider
from swarmauri_core.keys.types import KeySpec, KeyAlg

provider = VaultTransitKeyProvider(url="http://localhost:8200", token="root")
key = await provider.create_key(KeySpec(alg=KeyAlg.ED25519))
jwks = await provider.jwks()
```

## Configuration

The provider accepts several parameters:

- `url`: Vault server address
- `token`: authentication token
- `mount`: Transit engine mount point (default: `transit`)
- `namespace`: optional Vault namespace
- `verify`: TLS verification settings
- `prefer_vault_rng`: favor Vault for random byte generation

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md).
