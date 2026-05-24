![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_pop_dpop/">
        <img src="https://static.pepy.tech/badge/swarmauri_pop_dpop/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_pop_dpop/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_pop_dpop.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_pop_dpop/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Supported Python Versions"/></a>
    <a href="https://pypi.org/project/swarmauri_pop_dpop/">
        <img src="https://img.shields.io/pypi/l/swarmauri_pop_dpop" alt="License"/></a>
    <a href="https://pypi.org/project/swarmauri_pop_dpop/">
        <img src="https://img.shields.io/pypi/v/swarmauri_pop_dpop?label=swarmauri_pop_dpop&color=green" alt="Release Version"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a>
</p>

# Swarmauri PoP DPoP

DPoP proof-of-possession tooling for Swarmauri services.

## Features

- DPoP proof-of-possession tooling for Swarmauri services.
- Centers its public API around `DPoPSigner`, `DPoPVerifier` so downstream code can import the package directly without extra registry glue.
- Fits the standards package lane so the capability can be added to a project as a focused, separately versioned dependency.

## Installation

Install this package with `uv` or `pip`.

```bash
uv add swarmauri_pop_dpop
```

```bash
pip install swarmauri_pop_dpop
```

## Usage

Start by importing the public package surface, then configure the exported type or callable inside the workflow that consumes it.

```python
from swarmauri_pop_dpop import DPoPSigner, DPoPVerifier

exports = ['DPoPSigner', 'DPoPVerifier']
print(exports)
```

After import, pass the exported objects into the surrounding Swarmauri or Tigrbl code that owns configuration, credentials, transport, or storage details.

License: Apache-2.0. See `LICENSE`.
