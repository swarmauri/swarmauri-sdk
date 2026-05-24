![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_distance_manhattan/">
        <img src="https://static.pepy.tech/badge/swarmauri_distance_manhattan/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_distance_manhattan/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_distance_manhattan.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_distance_manhattan/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Supported Python Versions"/></a>
    <a href="https://pypi.org/project/swarmauri_distance_manhattan/">
        <img src="https://img.shields.io/pypi/l/swarmauri_distance_manhattan" alt="License"/></a>
    <a href="https://pypi.org/project/swarmauri_distance_manhattan/">
        <img src="https://img.shields.io/pypi/v/swarmauri_distance_manhattan?label=swarmauri_distance_manhattan&color=green" alt="Release Version"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a>
</p>

# Swarmauri Distance Manhattan

Deprecated standalone compatibility package for manhattan distance.

## Features

- Deprecated standalone compatibility package for manhattan distance.
- Preserves legacy imports and package boundaries so older integrations can keep running while you migrate to active packages.
- Fits the standards package lane so the capability can be added to a project as a focused, separately versioned dependency.

## Installation

Install this package with `uv` or `pip`.

```bash
uv add swarmauri_distance_manhattan
```

```bash
pip install swarmauri_distance_manhattan
```

## Usage

Use this package only as a compatibility bridge while moving callers onto active packages in the workspace.

```python
from swarmauri_distance_manhattan import PackageNotFoundError, version, ManhattanDistance

exports = ['PackageNotFoundError', 'version', 'ManhattanDistance']
print(exports)
```

Expect legacy imports to continue working, but plan migration work because the package is retained for compatibility rather than long-term growth.

License: Apache-2.0. See `LICENSE`.
