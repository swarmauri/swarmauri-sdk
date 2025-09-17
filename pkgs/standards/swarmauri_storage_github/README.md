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

`GithubStorageAdapter` is a lightweight placeholder storage adapter for Peagen.
It returns deterministic `github://` URIs for uploaded objects without making
any network calls to GitHub. The class is useful for demos, tests, and for
validating code paths that rely on the storage adapter interface.

## Installation

Choose the tool that matches your workflow:

```bash
# pip
pip install swarmauri_storage_github

# Poetry
poetry add swarmauri_storage_github

# uv
uv add swarmauri_storage_github
```

## Quickstart

`GithubStorageAdapter.upload()` accepts a key and a binary file-like object. It
returns the key formatted as a `github://` URI so callers can wire the adapter
into pipelines that expect GitHub-backed storage without performing any remote
I/O.

```python
from io import BytesIO

from swarmauri_storage_github import GithubStorageAdapter


adapter = GithubStorageAdapter()

# The adapter only inspects the key, so any binary stream is acceptable.
payload = BytesIO(b"# Example README\nThis payload would be uploaded to GitHub.")
uri = adapter.upload("my-org/my-repo/README.md", payload)

print(uri)  # github://my-org/my-repo/README.md
```

### Behavior and limitations

- `upload()` does not persist data—it simply echoes the key back as a
  `github://` URI.
- `download()`, `upload_dir()`, and `download_dir()` raise
  `NotImplementedError` to signal that full GitHub support is intentionally out
  of scope for this stub.
