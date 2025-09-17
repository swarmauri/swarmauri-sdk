![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_gitfilter_minio/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_gitfilter_minio" alt="PyPI - Downloads"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_gitfilter_minio/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_gitfilter_minio.svg"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_gitfilter_minio/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_gitfilter_minio" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_gitfilter_minio/">
        <img src="https://img.shields.io/pypi/l/swarmauri_gitfilter_minio" alt="PyPI - License"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_gitfilter_minio/">
        <img src="https://img.shields.io/pypi/v/swarmauri_gitfilter_minio?label=swarmauri_gitfilter_minio&color=green" alt="PyPI - swarmauri_gitfilter_minio"/>
    </a>
</p>

---

# Swarmauri Git Filter Minio

`swarmauri_gitfilter_minio` packages the `MinioFilter` plugin used by
[`peagen`](https://pypi.org/project/peagen/) and other Swarmauri tooling to keep
large Git objects in MinIO (or any S3-compatible) storage instead of the local
repository. The filter implements both `StorageAdapterBase` and
`GitFilterBase`, so you can call it directly from Python code or register it as
a Git clean/smudge filter.

### Highlights

- Accepts `minio://` (HTTP) and `minios://` (HTTPS) URIs and automatically
  ensures the referenced bucket exists.
- Inherits `GitFilterBase`, giving you `clean` and `smudge` helpers that hash
  content, upload it to remote storage, and hydrate it back into your working
  tree on checkout.
- Provides convenience methods such as `upload_dir`, `iter_prefix`, and
  `download_prefix` for whole directory trees in addition to single-file
  transfers.
- Surfaces a `root_uri` property that reflects the bucket and optional prefix
  derived from the connection string.

## Installation

Choose the workflow that matches your project:

```bash
# pip
pip install swarmauri_gitfilter_minio

# Poetry
poetry add swarmauri_gitfilter_minio

# uv
uv add swarmauri_gitfilter_minio
```

## Configuration

`MinioFilter.from_uri()` consults `peagen.toml` for credentials under
`[storage.filters.minio]` and falls back to the `MINIO_ACCESS_KEY` and
`MINIO_SECRET_KEY` environment variables when the configuration is absent. When
instantiated, the filter lazily creates the bucket identified by the URI and
stores objects beneath an optional prefix.

## Usage

```python
from swarmauri_gitfilter_minio import MinioFilter

# Create a filter from a connection string. The scheme `minios://` will use
# HTTPS while `minio://` uses plain HTTP.
filt = MinioFilter.from_uri("minio://localhost:9000/my-bucket/prefix")

# Upload a file and retrieve its URI
with open("README.md", "rb") as fh:
    uri = filt.upload("docs/README.md", fh)

# Download the file back into memory
buffer = filt.download("docs/README.md")
data = buffer.read()
```

`MinioFilter` also exposes helpers such as `upload_dir`, `iter_prefix`, and
`download_prefix` for working with entire directory trees.

## License

Licensed under the [Apache License, Version 2.0](LICENSE).
