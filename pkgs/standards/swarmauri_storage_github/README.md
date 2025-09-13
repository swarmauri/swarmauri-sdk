![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_storage_github/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_storage_github" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_storage_github/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_storage_github.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_storage_github/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_storage_github" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_storage_github/">
        <img src="https://img.shields.io/pypi/l/swarmauri_storage_github" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_storage_github/">
        <img src="https://img.shields.io/pypi/v/swarmauri_storage_github?label=swarmauri_storage_github&color=green" alt="PyPI - swarmauri_storage_github"/></a>

</p>

---

# Swarmauri GitHub Storage Adapter

Simplified storage adapter for Peagen that records uploads as `github://` URIs.

## Installation

```bash
# pip install swarmauri_storage_github (when published)
```

## Usage

```python
from swarmauri_storage_github import GithubStorageAdapter

adapter = GithubStorageAdapter()
uri = adapter.upload("README.md", "my-org/my-repo/README.md")
print(uri)
```
