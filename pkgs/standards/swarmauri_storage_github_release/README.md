![Swarmauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_storage_github_release/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_storage_github_release" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_storage_github_release/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_storage_github_release.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_storage_github_release/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_storage_github_release" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_storage_github_release/">
        <img src="https://img.shields.io/pypi/l/swarmauri_storage_github_release" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_storage_github_release/">
        <img src="https://img.shields.io/pypi/v/swarmauri_storage_github_release?label=swarmauri_storage_github_release&color=green" alt="PyPI - swarmauri_storage_github_release"/></a>

</p>

---

# Swarmauri GitHub Release Storage Adapter

Stores artifacts as assets on a GitHub release for use with Peagen.

## Installation

```bash
# pip install swarmauri_storage_github_release (when published)
```

## Usage

```python
from swarmauri_storage_github_release import GithubReleaseStorageAdapter
from pydantic import SecretStr
import io

adapter = GithubReleaseStorageAdapter(
    token=SecretStr("ghp_..."),
    org="my-org",
    repo="my-repo",
    tag="v1.0.0",
)
uri = adapter.upload("artifact.txt", io.BytesIO(b"data"))
print(uri)
```
