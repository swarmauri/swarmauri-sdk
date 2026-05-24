![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_typing/">
        <img src="https://static.pepy.tech/badge/swarmauri_typing/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/typing/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/typing.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_typing/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Supported Python Versions"/></a>
    <a href="https://pypi.org/project/swarmauri_typing/">
        <img src="https://img.shields.io/pypi/l/swarmauri_typing" alt="License"/></a>
    <a href="https://pypi.org/project/swarmauri_typing/">
        <img src="https://img.shields.io/pypi/v/swarmauri_typing?label=swarmauri_typing&color=green" alt="Release Version"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a>
</p>

# Swarmauri Typing

Dynamic typing utilities for Swarmauri annotated unions, intersection metadata, and registry-driven component models.

## Features

- Dynamic typing utilities for Swarmauri annotated unions, intersection metadata, and registry-driven component models.
- Centers its public API around `UnionFactory`, `UnionFactoryMetadata`, `Intersection`, `IntersectionMetadata` so downstream code can import the package directly without extra registry glue.
- Aligns with the current workspace packaging model so the package can participate cleanly in larger Swarmauri SDK builds.

## Installation

Install this package with `uv` or `pip`.

```bash
uv add swarmauri_typing
```

```bash
pip install swarmauri_typing
```

## Usage

Start by importing the public package surface, then configure the exported type or callable inside the workflow that consumes it.

```python
from swarmauri_typing import UnionFactory, UnionFactoryMetadata, Intersection, IntersectionMetadata

exports = ['UnionFactory', 'UnionFactoryMetadata', 'Intersection', 'IntersectionMetadata']
print(exports)
```

After import, pass the exported objects into the surrounding Swarmauri or Tigrbl code that owns configuration, credentials, transport, or storage details.

License: Apache-2.0. See `LICENSE`.
