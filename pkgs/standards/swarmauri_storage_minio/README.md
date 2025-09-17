![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_storage_minio/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_storage_minio" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_storage_minio/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_storage_minio.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_storage_minio/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_storage_minio" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_storage_minio/">
        <img src="https://img.shields.io/pypi/l/swarmauri_storage_minio" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_storage_minio/">
        <img src="https://img.shields.io/pypi/v/swarmauri_storage_minio?label=swarmauri_storage_minio&color=green" alt="PyPI - swarmauri_storage_minio"/></a>

</p>

---

# Swarmauri MinIO Storage Adapter

Peagen storage adapter that saves artifacts to a MinIO or any S3-compatible bucket using the official `minio` Python client.

## Features

- Automatically creates the target bucket if it does not already exist.
- Optional `prefix` argument to scope uploads without changing your keys.
- Implements `upload`, `download`, `upload_dir`, `download_dir`, and `iter_prefix` helpers for working with single files or directories.
- Exposes a `root_uri` describing the bucket and prefix (`minio[s]://endpoint/bucket/prefix/`).
- `MinioStorageAdapter.from_uri()` reads credentials from `peagen.toml` or the `MINIO_ACCESS_KEY` / `MINIO_SECRET_KEY` environment variables for zero-copy configuration.

## Installation

### Using uv

```bash
uv add swarmauri_storage_minio
# or install into an existing environment
uv pip install swarmauri_storage_minio
```

### Using Poetry

```bash
poetry add swarmauri_storage_minio
```

### Using pip

```bash
pip install swarmauri_storage_minio
```

## Usage

The adapter wraps a MinIO client instance. When you instantiate it, the bucket is created if it does not already exist. Use the `secure` flag for HTTPS endpoints (`True` by default) and supply a `prefix` when you want to namespace all uploads under a directory.

```python
from swarmauri_storage_minio import MinioStorageAdapter
import io

adapter = MinioStorageAdapter(
    endpoint="localhost:9000",
    access_key="minio",
    secret_key="minio123",
    bucket="peagen",
    secure=False,
    prefix="examples/",
)
uri = adapter.upload("artifact.txt", io.BytesIO(b"data"))
print(uri)

downloaded = adapter.download("artifact.txt").read()
print(downloaded.decode("utf-8"))
```

> **Note:** If you store credentials as `SecretStr`, call `.get_secret_value()` when passing them to the adapter.

### Config-driven instantiation

The adapter can also be created from a URI. Credentials are loaded from `peagen.toml` or environment variables.

```toml
# peagen.toml
[storage.adapters.minio]
access_key = "minio"
secret_key = "minio123"
```

```python
from swarmauri_storage_minio import MinioStorageAdapter

adapter = MinioStorageAdapter.from_uri("minio://localhost:9000/peagen/examples/")
print(adapter.root_uri)
```
