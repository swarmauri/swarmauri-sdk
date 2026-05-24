![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_core/">
        <img src="https://static.pepy.tech/badge/swarmauri_core/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/core/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/core.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_core/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Supported Python Versions"/></a>
    <a href="https://pypi.org/project/swarmauri_core/">
        <img src="https://img.shields.io/pypi/l/swarmauri_core" alt="License"/></a>
    <a href="https://pypi.org/project/swarmauri_core/">
        <img src="https://img.shields.io/pypi/v/swarmauri_core?label=swarmauri_core&color=green" alt="Release Version"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a>
</p>

# Swarmauri Core

Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

## Features

- Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.
- Keeps the package surface isolated so you can install only the capability you need instead of the full workspace.
- Aligns with the current workspace packaging model so the package can participate cleanly in larger Swarmauri SDK builds.

## Installation

Install this package with `uv` or `pip`.

```bash
uv add swarmauri_core
```

```bash
pip install swarmauri_core
```

## Usage

Start by importing the public package surface, then configure the exported type or callable inside the workflow that consumes it.

```python
import swarmauri_core

print(swarmauri_core.__name__)
```

After import, pass the exported objects into the surrounding Swarmauri or Tigrbl code that owns configuration, credentials, transport, or storage details.

License: Apache-2.0. See `LICENSE`.
