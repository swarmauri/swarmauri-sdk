![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/catoml/">
        <img src="https://static.pepy.tech/badge/catoml/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/catoml/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/catoml.svg"/></a>
    <a href="https://pypi.org/project/catoml/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Supported Python Versions"/></a>
    <a href="https://pypi.org/project/catoml/">
        <img src="https://img.shields.io/pypi/l/catoml" alt="License"/></a>
    <a href="https://pypi.org/project/catoml/">
        <img src="https://img.shields.io/pypi/v/catoml?label=catoml&color=green" alt="Release Version"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a>
</p>

# Catoml

Swarmauri's Canon Toml.

## Features

- Swarmauri's Canon Toml.
- Keeps the package surface isolated so you can install only the capability you need instead of the full workspace.
- Provides an experimental workspace surface for early validation before functionality graduates into a more stable package lane.

## Installation

Install this package with `uv` or `pip`.

```bash
uv add catoml
```

```bash
pip install catoml
```

## Usage

Start by importing the public package surface, then configure the exported type or callable inside the workflow that consumes it.

```python
import catoml

print(catoml.__name__)
```

After import, pass the exported objects into the surrounding Swarmauri or Tigrbl code that owns configuration, credentials, transport, or storage details.

License: Apache-2.0. See `LICENSE`.
