![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_storage_s3fs/">
        <img src="https://static.pepy.tech/badge/swarmauri_storage_s3fs/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_storage_s3fs/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_storage_s3fs.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_storage_s3fs/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Supported Python Versions"/></a>
    <a href="https://pypi.org/project/swarmauri_storage_s3fs/">
        <img src="https://img.shields.io/pypi/l/swarmauri_storage_s3fs" alt="License"/></a>
    <a href="https://pypi.org/project/swarmauri_storage_s3fs/">
        <img src="https://img.shields.io/pypi/v/swarmauri_storage_s3fs?label=swarmauri_storage_s3fs&color=green" alt="Release Version"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a>
</p>

# Swarmauri Storage S3FS

Filesystem-style S3 storage adapter for SwarmauriSDK backed strictly by `s3fs`.

## Features

- Stores and retrieves objects from `s3://` locations through `s3fs.S3FileSystem`.
- Supports S3-compatible endpoints through `endpoint_url` and `client_kwargs`.
- Provides discoverable `swarmauri.storage_adapters` and `peagen.plugins.storage_adapters` entry points.
- Handles object upload, download, range reads, prefix iteration, directory push/pull, bucket creation, and object removal.

## Installation

Install this package with `uv` or `pip`.

```bash
uv add swarmauri_storage_s3fs
```

```bash
pip install swarmauri_storage_s3fs
```

## Usage

Use this adapter when the workflow should use the `s3fs` filesystem API.

```python
from swarmauri_storage_s3fs import S3FSStorageAdapter

adapter = S3FSStorageAdapter.from_uri("s3://model-artifacts/runs")
uri = adapter.put_blob("latest/result.json", b'{"status":"ok"}')
payload = adapter.get_blob("latest/result.json")

print(uri)
print(payload)
```

Configure credentials through `s3fs`, environment variables, or explicit constructor arguments owned by the surrounding Swarmauri or Tigrbl workflow.

License: Apache-2.0. See `LICENSE`.
