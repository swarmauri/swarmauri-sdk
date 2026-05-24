![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_gitfilter_file/">
        <img src="https://static.pepy.tech/badge/swarmauri_gitfilter_file/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_gitfilter_file/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_gitfilter_file.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_gitfilter_file/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Supported Python Versions"/></a>
    <a href="https://pypi.org/project/swarmauri_gitfilter_file/">
        <img src="https://img.shields.io/pypi/l/swarmauri_gitfilter_file" alt="License"/></a>
    <a href="https://pypi.org/project/swarmauri_gitfilter_file/">
        <img src="https://img.shields.io/pypi/v/swarmauri_gitfilter_file?label=swarmauri_gitfilter_file&color=green" alt="Release Version"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a>
</p>

# Swarmauri Gitfilter File

Filesystem git filter for Peagen.

## Features

- Filesystem git filter for Peagen.
- Exposes discoverable runtime entry points for `peagen.plugins.git_filters, swarmauri.git_filters` so the package can be wired into Swarmauri or Tigrbl workflows.
- Fits the standards package lane so the capability can be added to a project as a focused, separately versioned dependency.

## Installation

Install this package with `uv` or `pip`.

```bash
uv add swarmauri_gitfilter_file
```

```bash
pip install swarmauri_gitfilter_file
```

## Usage

Start by importing the public package surface, then configure the exported type or callable inside the workflow that consumes it.

```python
from swarmauri_gitfilter_file import FileFilter

exports = ['FileFilter']
print(exports)
```

After import, pass the exported objects into the surrounding Swarmauri or Tigrbl code that owns configuration, credentials, transport, or storage details.

License: Apache-2.0. See `LICENSE`.
