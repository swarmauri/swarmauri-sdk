![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_storage_minio/">
        <img src="https://static.pepy.tech/badge/swarmauri_storage_minio/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_storage_minio/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_storage_minio.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_storage_minio/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_storage_minio/">
        <img src="https://img.shields.io/pypi/l/swarmauri_storage_minio" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_storage_minio/">
        <img src="https://img.shields.io/pypi/v/swarmauri_storage_minio?label=swarmauri_storage_minio&color=green" alt="PyPI - swarmauri_storage_minio"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri MinIO Storage Adapter

Peagen storage adapter that saves artifacts to a MinIO or any S3-compatible bucket using the official `minio` Python client.

## Features

- Automatically creates the target bucket if it does not already exist.
- Optional `prefix` argument to scope uploads without changing your keys.
- Implements `upload`, `download`, `upload_dir`, `download_dir`, and `iter_prefix` helpers for working with single files or directories.
- Adds `upload_memoryview`, `download_memoryview`, `upload_mmap`, and `open_mmap` helpers for zero-copy byte workflows.
- Exposes a `root_uri` describing the bucket and prefix (`minio[s]://endpoint/bucket/prefix/`).
- `MinioStorageAdapter.from_uri()` reads credentials from `MINIO_ACCESS_KEY` and `MINIO_SECRET_KEY` environment variables for zero-copy configuration.

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

The adapter can also be created from a URI. Credentials are loaded from environment variables.

```python
from swarmauri_storage_minio import MinioStorageAdapter

adapter = MinioStorageAdapter.from_uri("minio://localhost:9000/peagen/examples/")
print(adapter.root_uri)
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.

