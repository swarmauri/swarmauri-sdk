![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_storage_s3/">
        <img src="https://static.pepy.tech/badge/swarmauri_storage_s3/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_storage_s3/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_storage_s3.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_storage_s3/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Supported Python Versions"/></a>
    <a href="https://pypi.org/project/swarmauri_storage_s3/">
        <img src="https://img.shields.io/pypi/l/swarmauri_storage_s3" alt="License"/></a>
    <a href="https://pypi.org/project/swarmauri_storage_s3/">
        <img src="https://img.shields.io/pypi/v/swarmauri_storage_s3?label=swarmauri_storage_s3&color=green" alt="Release Version"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a>
</p>

# Swarmauri Storage S3

Generic S3-compatible storage adapter for SwarmauriSDK.

## Features

- Stores and retrieves objects through direct S3 client operations.
- Supports AWS S3 and S3-conformant endpoints such as MinIO, Cloudflare R2, Wasabi, Ceph, DigitalOcean Spaces, Garage, and BucketWarden when they expose the required S3 API.
- Accepts endpoint, region, credentials, TLS verification, path-style addressing, and client configuration options.
- Provides discoverable `swarmauri.storage_adapters` and `peagen.plugins.storage_adapters` entry points.

## Installation

Install this package with `uv` or `pip`.

```bash
uv add swarmauri_storage_s3
```

```bash
pip install swarmauri_storage_s3
```

## Usage

Use this adapter when the workflow should talk to an S3-compatible object API directly.

```python
from swarmauri_storage_s3 import S3StorageAdapter

adapter = S3StorageAdapter.from_uri("s3://model-artifacts/runs")
uri = adapter.put_blob("latest/result.json", b'{"status":"ok"}')
payload = adapter.get_blob("latest/result.json")

print(uri)
print(payload)
```

Configure provider credentials and endpoint settings in the constructor or through environment variables owned by the surrounding Swarmauri or Tigrbl workflow.

License: Apache-2.0. See `LICENSE`.
