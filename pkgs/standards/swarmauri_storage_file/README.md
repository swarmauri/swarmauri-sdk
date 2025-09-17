![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_storage_file/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_storage_file" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_storage_file/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_storage_file.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_storage_file/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_storage_file" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_storage_file/">
        <img src="https://img.shields.io/pypi/l/swarmauri_storage_file" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_storage_file/">
        <img src="https://img.shields.io/pypi/v/swarmauri_storage_file?label=swarmauri_storage_file&color=green" alt="PyPI - swarmauri_storage_file"/></a>

</p>

---

# Swarmauri File Storage Adapter

Filesystem-based storage adapter for Peagen that stores binary artifacts on the
local disk.

## Features

- Resolves and prepares the configured ``output_dir`` on instantiation so
  uploads can run without additional filesystem setup.
- Supports an optional ``prefix`` to scope all keys inside a nested directory
  tree while keeping the same adapter instance.
- ``upload`` writes files atomically by copying into a temporary file before an
  atomic rename, ensuring partially written data is never observed.
- ``download`` returns a :class:`io.BytesIO` handle positioned at the start of
  the stored content for immediate consumption by downstream tooling.
- Convenience helpers such as ``upload_dir``, ``download_dir``, ``iter_prefix``
  and ``from_uri`` mirror the behavior of :class:`pathlib.Path` operations and
  make it easy to bulk transfer artifacts.
- ``root_uri`` exposes the workspace as a ``file://`` URI which is used when
  constructing the URIs returned by ``upload``.

## Installation

Install the package with your preferred Python packaging tool:

```bash
pip install swarmauri_storage_file
```

```bash
poetry add swarmauri_storage_file
```

```bash
uv pip install swarmauri_storage_file
```

## Usage

```python
from pathlib import Path
import io

from swarmauri_storage_file import FileStorageAdapter

workspace = Path("./artifacts").resolve()
adapter = FileStorageAdapter(output_dir=workspace)

root_uri = adapter.root_uri
print("Root URI:", root_uri)

uri = adapter.upload("example.txt", io.BytesIO(b"hello world"))
print("Stored at:", uri)

downloaded = adapter.download("example.txt").read().decode("utf-8")
print("Contents:", downloaded)

keys = list(adapter.iter_prefix(""))
print("Keys:", keys)
```

The snippet above resolves a local workspace, uploads an artifact, reads it
back as text and inspects the stored keys.  URIs returned by ``upload`` reuse
``root_uri`` (with the relative key appended) so they can be dereferenced by
tools that understand ``file://`` locations.

### Additional helpers

- ``upload_dir`` recursively walks a source directory and stores each file
  under an optional destination prefix.
- ``download_dir`` materializes a stored prefix into a destination directory,
  recreating any nested structure.
- ``iter_prefix`` yields keys rooted at ``output_dir`` (including any configured
  prefix) which is useful for inventory or cleanup tasks.
- ``from_uri`` rebuilds an adapter from a ``file://`` URI previously emitted by
  ``root_uri`` or ``upload``.
