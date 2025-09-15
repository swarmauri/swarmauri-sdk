![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)


<p align="center">
    <a href="https://pypi.org/project/swarmauri_keyproviders_mirrored/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_keyproviders_mirrored" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_keyproviders_mirrored/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_keyproviders_mirrored.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_keyproviders_mirrored/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_keyproviders_mirrored" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_keyproviders_mirrored/">
        <img src="https://img.shields.io/pypi/l/swarmauri_keyproviders_mirrored" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_keyproviders_mirrored/">
        <img src="https://img.shields.io/pypi/v/swarmauri_keyproviders_mirrored?label=swarmauri_keyproviders_mirrored&color=green" alt="PyPI - swarmauri_keyproviders_mirrored"/></a>
</p>

---

# Swarmauri Mirrored Key Provider

A failover key provider that mirrors keys to a secondary provider for redundancy.
Supports full and public-only replication with optional extras for canonical
representations.

Features:
- Mirror new keys to a secondary provider
- Failover reads when the primary provider is unavailable
- JWKS union merging as described in RFC 7517
- Optional extras for JSON and CBOR canonicalization

## Installation

```bash
pip install swarmauri_keyproviders_mirrored
```

## Usage

```python
from swarmauri_keyproviders_mirrored import MirroredKeyProvider
from swarmauri_keyprovider_local import LocalKeyProvider

primary = LocalKeyProvider()
secondary = LocalKeyProvider()
provider = MirroredKeyProvider(primary, secondary)
```

## Entry Point

The provider registers under the `swarmauri.key_providers` entry point as
`MirroredKeyProvider`.

