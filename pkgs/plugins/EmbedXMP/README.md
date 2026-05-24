![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/EmbedXMP/">
        <img src="https://static.pepy.tech/badge/EmbedXMP/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/plugins/EmbedXMP/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/plugins/EmbedXMP.svg"/></a>
    <a href="https://pypi.org/project/EmbedXMP/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Supported Python Versions"/></a>
    <a href="https://pypi.org/project/EmbedXMP/">
        <img src="https://img.shields.io/pypi/l/EmbedXMP" alt="License"/></a>
    <a href="https://pypi.org/project/EmbedXMP/">
        <img src="https://img.shields.io/pypi/v/EmbedXMP?label=EmbedXMP&color=green" alt="Release Version"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a>
</p>

# EmbedXMP

Dynamic XMP embed/read/remove orchestration for Swarmauri handlers.

## Features

- Dynamic XMP embed/read/remove orchestration for Swarmauri handlers.
- Centers its public API around `Path`, `Iterable`, `List`, `Sequence` so downstream code can import the package directly without extra registry glue.
- Supports direct plugin instantiation from application code; avoid `PluginManager` unless a task explicitly requires it.

## Installation

Install this package with `uv` or `pip`.

```bash
uv add EmbedXMP
```

```bash
pip install EmbedXMP
```

## Usage

Instantiate the exported plugin classes directly in your application or test harness. Do not route plugin setup through `PluginManager` unless you were explicitly asked to do so.

```python
from EmbedXMP import Path, Iterable, List, Sequence

exports = ['Path', 'Iterable', 'List', 'Sequence']
print(exports)
```

After import, pass the exported objects into the surrounding Swarmauri or Tigrbl code that owns configuration, credentials, transport, or storage details.

License: Apache-2.0. See `LICENSE`.
