![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_storage_memory/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_storage_memory" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_storage_memory/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_storage_memory.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_storage_memory/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_storage_memory" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_storage_memory/">
        <img src="https://img.shields.io/pypi/l/swarmauri_storage_memory" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_storage_memory/">
        <img src="https://img.shields.io/pypi/v/swarmauri_storage_memory?label=swarmauri_storage_memory&color=green" alt="PyPI - swarmauri_storage_memory"/></a>

</p>

---

# Swarmauri Memory Storage Adapter

In-memory storage adapter for SwarmauriSDK workflows. This adapter is ideal for
unit tests, demos, or short-lived workloads where you want to avoid persistent
storage and rely entirely on process memory.

## Features

- Keeps uploaded artifacts in an in-memory dictionary for fast access.
- Supports optional key prefixes to scope uploads and downloads.
- Provides helper methods for bulk upload/download operations.
- Emits ``memory://`` URIs so downstream components can trace stored artifacts.
- Supports Python 3.10 through 3.12.

## Installation

Install the package with your preferred Python packaging tool:

```bash
uv pip install swarmauri_storage_memory
```

```bash
pip install swarmauri_storage_memory
```

## Usage

```python
import io

from swarmauri_storage_memory import MemoryStorageAdapter

adapter = MemoryStorageAdapter(prefix="session")

uri = adapter.upload("example.txt", io.BytesIO(b"hello"))
print("Stored at:", uri)

downloaded = adapter.download("example.txt").read().decode("utf-8")
print("Contents:", downloaded)

keys = list(adapter.iter_prefix(""))
print("Keys:", keys)
```

The adapter above stores data purely in memory, making it suitable for
lightweight or ephemeral workflows. Use ``upload_dir`` and ``download_dir`` for
bulk transfers when you need to stage many artifacts in memory at once.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.
