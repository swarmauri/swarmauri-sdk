![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_tests_loc_tersity/">
        <img src="https://static.pepy.tech/badge/swarmauri_tests_loc_tersity/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/swarmauri_tests_loc_tersity/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/swarmauri_tests_loc_tersity.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tests_loc_tersity/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Supported Python Versions"/></a>
    <a href="https://pypi.org/project/swarmauri_tests_loc_tersity/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tests_loc_tersity" alt="License"/></a>
    <a href="https://pypi.org/project/swarmauri_tests_loc_tersity/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tests_loc_tersity?label=swarmauri_tests_loc_tersity&color=green" alt="Release Version"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a>
</p>

# Swarmauri Tests Loc Tersity

Pytest plugin enforcing line count limits.

## Features

- Pytest plugin enforcing line count limits.
- Exposes discoverable runtime entry points for `pytest11` so the package can be wired into Swarmauri or Tigrbl workflows.
- Provides an experimental workspace surface for early validation before functionality graduates into a more stable package lane.

## Installation

Install this package with `uv` or `pip`.

```bash
uv add swarmauri_tests_loc_tersity
```

```bash
pip install swarmauri_tests_loc_tersity
```

## Usage

Start by importing the public package surface, then configure the exported type or callable inside the workflow that consumes it.

```python
from swarmauri_tests_loc_tersity import Path

exports = ['Path']
print(exports)
```

After import, pass the exported objects into the surrounding Swarmauri or Tigrbl code that owns configuration, credentials, transport, or storage details.

License: Apache-2.0. See `LICENSE`.
