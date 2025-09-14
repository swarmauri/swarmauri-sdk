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

Filesystem-based storage adapter for Peagen that stores artifacts on the local disk.

## Installation

```bash
# pip install swarmauri_storage_file (when published)
```

## Usage

```python
from swarmauri_storage_file import FileStorageAdapter
import io

adapter = FileStorageAdapter(output_dir="/tmp/peagen")
uri = adapter.upload("example.txt", io.BytesIO(b"hello"))
print("Stored at", uri)
```
