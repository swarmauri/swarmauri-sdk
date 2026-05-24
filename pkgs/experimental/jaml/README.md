![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/jaml/">
        <img src="https://static.pepy.tech/badge/jaml/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/jaml/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/jaml.svg"/></a>
    <a href="https://pypi.org/project/jaml/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Supported Python Versions"/></a>
    <a href="https://pypi.org/project/jaml/">
        <img src="https://img.shields.io/pypi/l/jaml" alt="License"/></a>
    <a href="https://pypi.org/project/jaml/">
        <img src="https://img.shields.io/pypi/v/jaml?label=jaml&color=green" alt="Release Version"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a>
</p>

# Jaml

Swarmauri's Canon Jaml Handler.

## Features

- Swarmauri's Canon Jaml Handler.
- Centers its public API around `dump`, `dumps`, `load`, `loads` so downstream code can import the package directly without extra registry glue.
- Provides an experimental workspace surface for early validation before functionality graduates into a more stable package lane.

## Installation

Install this package with `uv` or `pip`.

```bash
uv add jaml
```

```bash
pip install jaml
```

## Usage

Start by importing the public package surface, then configure the exported type or callable inside the workflow that consumes it.

```python
from jaml import dump, dumps, load, loads

exports = ['dump', 'dumps', 'load', 'loads']
print(exports)
```

After import, pass the exported objects into the surrounding Swarmauri or Tigrbl code that owns configuration, credentials, transport, or storage details.

License: Apache-2.0. See `LICENSE`.
