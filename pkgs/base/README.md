![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_base/">
        <img src="https://static.pepy.tech/badge/swarmauri_base/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/base/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/base.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_base/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Supported Python Versions"/></a>
    <a href="https://pypi.org/project/swarmauri_base/">
        <img src="https://img.shields.io/pypi/l/swarmauri_base" alt="License"/></a>
    <a href="https://pypi.org/project/swarmauri_base/">
        <img src="https://img.shields.io/pypi/v/swarmauri_base?label=swarmauri_base&color=green" alt="Release Version"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a>
</p>

# Swarmauri Base

Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.

## Features

- Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- Centers its public API around `SubclassUnion`, `FullUnion`, `register_model`, `register_type` so downstream code can import the package directly without extra registry glue.
- Aligns with the current workspace packaging model so the package can participate cleanly in larger Swarmauri SDK builds.

## Installation

Install this package with `uv` or `pip`.

```bash
uv add swarmauri_base
```

```bash
pip install swarmauri_base
```

## Usage

Start by importing the public package surface, then configure the exported type or callable inside the workflow that consumes it.

```python
from swarmauri_base import SubclassUnion, FullUnion, register_model, register_type

exports = ['SubclassUnion', 'FullUnion', 'register_model', 'register_type']
print(exports)
```

After import, pass the exported objects into the surrounding Swarmauri or Tigrbl code that owns configuration, credentials, transport, or storage details.

License: Apache-2.0. See `LICENSE`.
