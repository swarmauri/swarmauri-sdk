![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_certs_cfssl/">
        <img src="https://static.pepy.tech/badge/swarmauri_certs_cfssl/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certs_cfssl/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certs_cfssl.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_cfssl/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Supported Python Versions"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_cfssl/">
        <img src="https://img.shields.io/pypi/l/swarmauri_certs_cfssl" alt="License"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_cfssl/">
        <img src="https://img.shields.io/pypi/v/swarmauri_certs_cfssl?label=swarmauri_certs_cfssl&color=green" alt="Release Version"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a>
</p>

# Swarmauri Certs CFSSL

CFSSL REST backed Swarmauri certificate service for CSR signing, bundle verification, PEM/DER conversion, and X.509 parsing.

## Features

- CFSSL REST backed Swarmauri certificate service for CSR signing, bundle verification, PEM/DER conversion, and X.509 parsing.
- Exposes discoverable runtime entry points for `swarmauri.cert_services` so the package can be wired into Swarmauri or Tigrbl workflows.
- Lives in the community package lane for optional integrations that extend the main Swarmauri SDK surface.

## Installation

Install this package with `uv` or `pip`.

```bash
uv add swarmauri_certs_cfssl
```

```bash
pip install swarmauri_certs_cfssl
```

## Usage

Start by importing the public package surface, then configure the exported type or callable inside the workflow that consumes it.

```python
from swarmauri_certs_cfssl import CfsslCertService

exports = ['CfsslCertService']
print(exports)
```

After import, pass the exported objects into the surrounding Swarmauri or Tigrbl code that owns configuration, credentials, transport, or storage details.

License: Apache-2.0. See `LICENSE`.
