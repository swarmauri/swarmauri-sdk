![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/EmbeddedSigner/">
        <img src="https://static.pepy.tech/badge/EmbeddedSigner/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/plugins/embedded_signer/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/plugins/embedded_signer.svg"/></a>
    <a href="https://pypi.org/project/EmbeddedSigner/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Supported Python Versions"/></a>
    <a href="https://pypi.org/project/EmbeddedSigner/">
        <img src="https://img.shields.io/pypi/l/EmbeddedSigner" alt="License"/></a>
    <a href="https://pypi.org/project/EmbeddedSigner/">
        <img src="https://img.shields.io/pypi/v/EmbeddedSigner?label=EmbeddedSigner&color=green" alt="Release Version"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a>
</p>

# EmbeddedSigner

Embed XMP metadata and sign media assets using Swarmauri plugins.

## Features

- Embed XMP metadata and sign media assets using Swarmauri plugins.
- Ships with a package-local command or integration surface that can be installed independently from the rest of the workspace.
- Supports direct plugin instantiation from application code; avoid `PluginManager` unless a task explicitly requires it.

## Installation

Install this package with `uv` or `pip`.

```bash
uv add EmbeddedSigner
```

```bash
pip install EmbeddedSigner
```

## Usage

Instantiate the exported plugin classes directly in your application or test harness. Do not route plugin setup through `PluginManager` unless you were explicitly asked to do so.

```python
from EmbeddedSigner import EmbedSigner

exports = ['EmbedSigner']
print(exports)
```

Installed command-line entry points: `embedded-signer`.

License: Apache-2.0. See `LICENSE`.
