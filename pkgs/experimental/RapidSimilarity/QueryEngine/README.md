![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/QueryEngine/">
        <img src="https://static.pepy.tech/badge/QueryEngine/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/RapidSimilarity/QueryEngine/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/RapidSimilarity/QueryEngine.svg"/></a>
    <a href="https://pypi.org/project/QueryEngine/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Supported Python Versions"/></a>
    <a href="https://pypi.org/project/QueryEngine/">
        <img src="https://img.shields.io/pypi/l/QueryEngine" alt="License"/></a>
    <a href="https://pypi.org/project/QueryEngine/">
        <img src="https://img.shields.io/pypi/v/QueryEngine?label=QueryEngine&color=green" alt="Release Version"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a>
</p>

# QueryEngine

Configuration for package QueryEngine with C++ extensions using Meson build system.

## Features

- Configuration for package QueryEngine with C++ extensions using Meson build system.
- Centers its public API around `exact_query`, `approx_query` so downstream code can import the package directly without extra registry glue.
- Provides an experimental workspace surface for early validation before functionality graduates into a more stable package lane.

## Installation

Install this package with `uv` or `pip`.

```bash
uv add QueryEngine
```

```bash
pip install QueryEngine
```

## Usage

Start by importing the public package surface, then configure the exported type or callable inside the workflow that consumes it.

```python
from QueryEngine import exact_query, approx_query

exports = ['exact_query', 'approx_query']
print(exports)
```

After import, pass the exported objects into the surrounding Swarmauri or Tigrbl code that owns configuration, credentials, transport, or storage details.

License: Apache-2.0. See `LICENSE`.
