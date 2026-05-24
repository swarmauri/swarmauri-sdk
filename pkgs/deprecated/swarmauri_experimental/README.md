![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_experimental/">
        <img src="https://static.pepy.tech/badge/swarmauri_experimental/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/deprecated/swarmauri_experimental/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/deprecated/swarmauri_experimental.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_experimental/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Supported Python Versions"/></a>
    <a href="https://pypi.org/project/swarmauri_experimental/">
        <img src="https://img.shields.io/pypi/l/swarmauri_experimental" alt="License"/></a>
    <a href="https://pypi.org/project/swarmauri_experimental/">
        <img src="https://img.shields.io/pypi/v/swarmauri_experimental?label=swarmauri_experimental&color=green" alt="Release Version"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a>
</p>

# Swarmauri Experimental

This repository includes experimental components. (Inactive: experimental packages are now standalone.).

## Features

- This repository includes experimental components. (Inactive: experimental packages are now standalone.).
- Preserves legacy imports and package boundaries so older integrations can keep running while you migrate to active packages.
- Aligns with the current workspace packaging model so the package can participate cleanly in larger Swarmauri SDK builds.

## Installation

Install this package with `uv` or `pip`.

```bash
uv add swarmauri_experimental
```

```bash
pip install swarmauri_experimental
```

## Usage

Use this package only as a compatibility bridge while moving callers onto active packages in the workspace.

```python
import swarmauri_experimental

print(swarmauri_experimental.__name__)
```

Expect legacy imports to continue working, but plan migration work because the package is retained for compatibility rather than long-term growth.

License: Apache-2.0. See `LICENSE`.
