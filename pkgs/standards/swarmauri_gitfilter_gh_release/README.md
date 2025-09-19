![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_gitfilter_gh_release/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_gitfilter_gh_release" alt="PyPI - Downloads"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_gitfilter_gh_release/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_gitfilter_gh_release.svg"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_gitfilter_gh_release/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_gitfilter_gh_release" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_gitfilter_gh_release/">
        <img src="https://img.shields.io/pypi/l/swarmauri_gitfilter_gh_release" alt="PyPI - License"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_gitfilter_gh_release/">
        <img src="https://img.shields.io/pypi/v/swarmauri_gitfilter_gh_release?label=swarmauri_gitfilter_gh_release&color=green" alt="PyPI - swarmauri_gitfilter_gh_release"/>
    </a>
</p>

---

# Swarmauri Git Filter GitHub Release

Store artifacts in GitHub Releases.

## Overview

`swarmauri_gitfilter_gh_release` provides the `GithubReleaseFilter`, a `StorageAdapter` and `GitFilter` hybrid that manages Peagen artifacts as assets attached to a GitHub Release. It:

- Connects to the configured organization, repository, and release tag using [PyGithub](https://pygithub.readthedocs.io/).
- Creates the release on-demand if it does not already exist.
- Normalizes object keys with an optional prefix, exposing the release contents as a virtual directory via `root_uri`.
- Uploads and replaces release assets atomically, allowing you to store binary artifacts without worrying about duplicates.
- Supports directory workflows with `upload_dir`, `iter_prefix`, and `download_prefix` helpers for batch operations.

## Authentication & configuration

The filter authenticates using a GitHub token sourced from your `.peagen.toml` or the `GITHUB_TOKEN` environment variable. The token needs permissions to read and write releases in the target repository.

Example `.peagen.toml` snippet:

```toml
[storage.filters.gh_release]
token = "$GITHUB_TOKEN"
```

You can also set the environment variable directly:

```bash
export GITHUB_TOKEN="ghp_..."
```

## Installation

### pip

```bash
pip install swarmauri_gitfilter_gh_release
```

### uv

```bash
curl -Ls https://astral.sh/uv/install.sh | sh
uv pip install swarmauri_gitfilter_gh_release
```

### Poetry

```bash
poetry add swarmauri_gitfilter_gh_release
```

## Usage

```python
from swarmauri_gitfilter_gh_release import GithubReleaseFilter

filt = GithubReleaseFilter.from_uri("ghrel://org/repo/tag/artifacts")

print(filt.root_uri)
```

The example above resolves the release (creating it if necessary) and prints the normalized root URI (`ghrel://org/repo/tag/artifacts/`).

### Managing artifacts

`GithubReleaseFilter` mirrors GitHub release assets onto local paths. Each method accepts keys relative to the virtual root defined by the release tag and optional prefix:

- `upload(key, data)` uploads a file-like object and replaces existing assets that share the same key.
- `download(key)` streams a release asset back as a `BytesIO` object for inspection or local persistence.
- `upload_dir(path, prefix="")` walks a directory tree and pushes each file into the release using the provided prefix.
- `iter_prefix(prefix)` yields keys that start with the supplied prefix, allowing selective sync logic.
- `download_prefix(prefix, dest_dir)` restores a tree of assets into a target directory on disk.

Combine these helpers to move trained models, prompts, or configuration bundles between local development and persistent release storage while keeping file layouts consistent.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.