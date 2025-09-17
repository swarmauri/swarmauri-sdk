![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

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

Stores and retrieves artifacts as assets on a GitHub release. The adapter is
designed to plug directly into the Swarmauri/Peagen storage interfaces while
still being usable as a standalone utility.

## Features

- **Automatic release management** – a release is created on-demand when the
  requested tag does not already exist.
- **`ghrel://` addressing** – the adapter exposes a `root_uri` and returns
  fully-qualified URIs (e.g. `ghrel://org/repo/tag/path`) from `upload` calls.
- **Prefix-aware paths** – supply an optional `prefix` to group related assets
  underneath a pseudo-directory on the release.
- **Bulk helpers** – use `upload_dir` and `download_dir` to synchronise entire
  directories, or `iter_prefix` to discover stored assets.
- **Configuration friendly** – `GithubReleaseStorageAdapter.from_uri` reads
  credentials from `peagen.toml` (via `storage.adapters.gh_release.token`) or
  the `GITHUB_TOKEN` environment variable, enabling zero-code configuration in
  workflows.

## Requirements

- A GitHub personal access token (PAT) or GitHub App token with sufficient
  permissions to view, create and manage releases on the target repository.
- Network access to the GitHub REST API (provided by `PyGithub`).
- Python 3.10 through 3.12.

## Installation

### Install uv (optional)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Add the package with uv

```bash
uv add swarmauri_storage_github_release
```

### Add with Poetry

```bash
poetry add swarmauri_storage_github_release
```

### Install with pip

```bash
pip install swarmauri_storage_github_release
```

## Usage

```python
from io import BytesIO

from pydantic import SecretStr

from swarmauri_storage_github_release import GithubReleaseStorageAdapter

adapter = GithubReleaseStorageAdapter(
    token=SecretStr("ghp_example-token"),
    org="example-org",
    repo="example-repo",
    tag="v1.0.0",
    prefix="artifacts",
    release_name="Example release",
    message="Artifacts published by our workflow.",
)

print(adapter.root_uri)

uri = adapter.upload("artifact.txt", BytesIO(b"important payload"))
downloaded_payload = adapter.download("artifact.txt").read()
assets = list(adapter.iter_prefix(""))

print(uri)
print(downloaded_payload)
print(assets)
```

The code above demonstrates:

- `SecretStr` support for securely passing tokens.
- Automatic release creation when the `v1.0.0` tag does not exist.
- Prefix-aware uploads that produce the URI
  `ghrel://example-org/example-repo/v1.0.0/artifacts/artifacts/artifact.txt`
  (the asset key itself contains the prefix, so it appears in the base URI and
  the returned asset key).
- Round-tripping an asset and enumerating stored keys via `iter_prefix`.

## Working with directories

Use the bulk helper methods to synchronise entire directory trees:

```python
adapter.upload_dir("dist", prefix="binaries")
adapter.download_dir("binaries", "./downloads")
```

Both helpers respect the adapter-level prefix and will mirror nested folders.

## Using `ghrel://` URIs and configuration

The `from_uri` class method creates adapters from an address such as:

```python
adapter = GithubReleaseStorageAdapter.from_uri(
    "ghrel://example-org/example-repo/v1.0.0/artifacts",
)
```

When invoked this way the adapter resolves credentials from, in order:

1. `storage.adapters.gh_release.token` in `peagen.toml`.
2. The `GITHUB_TOKEN` environment variable.

Any prefix encoded in the URI is respected, and the resulting instance exposes
the same API shown above.

### Controlling release metadata

The constructor accepts additional keyword arguments to fine tune release
creation, including `release_name`, `message`, `draft`, and `prerelease`. These
parameters map directly to GitHub's release settings, allowing you to reuse the
adapter for production, staging, or nightly build workflows.
