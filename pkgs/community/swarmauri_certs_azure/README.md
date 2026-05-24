![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_certs_azure/">
        <img src="https://static.pepy.tech/badge/swarmauri_certs_azure/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certs_azure/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certs_azure.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_azure/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Supported Python Versions"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_azure/">
        <img src="https://img.shields.io/pypi/l/swarmauri_certs_azure" alt="License"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_azure/">
        <img src="https://img.shields.io/pypi/v/swarmauri_certs_azure?label=swarmauri_certs_azure&color=green" alt="Release Version"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a>
</p>

# Swarmauri Certs Azure

Azure Key Vault oriented Swarmauri certificate service for PKCS#10 CSR generation, PEM formatting, and certificate workflow helpers.

## Features

- Azure Key Vault oriented Swarmauri certificate service for PKCS#10 CSR generation, PEM formatting, and certificate workflow helpers.
- Keeps the package surface isolated so you can install only the capability you need instead of the full workspace.
- Lives in the community package lane for optional integrations that extend the main Swarmauri SDK surface.

## Installation

Install this package with `uv` or `pip`.

```bash
uv add swarmauri_certs_azure
```

```bash
pip install swarmauri_certs_azure
```

## Usage

Start by importing the public package surface, then configure the exported type or callable inside the workflow that consumes it.

```python
import swarmauri_certs_azure

print(swarmauri_certs_azure.__name__)
```

After import, pass the exported objects into the surrounding Swarmauri or Tigrbl code that owns configuration, credentials, transport, or storage details.

License: Apache-2.0. See `LICENSE`.
