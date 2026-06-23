![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_storage_s3_over_sftp/">
        <img src="https://static.pepy.tech/badge/swarmauri_storage_s3_over_sftp/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_storage_s3_over_sftp/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_storage_s3_over_sftp.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_storage_s3_over_sftp/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Supported Python Versions"/></a>
    <a href="https://pypi.org/project/swarmauri_storage_s3_over_sftp/">
        <img src="https://img.shields.io/pypi/l/swarmauri_storage_s3_over_sftp" alt="License"/></a>
    <a href="https://pypi.org/project/swarmauri_storage_s3_over_sftp/">
        <img src="https://img.shields.io/pypi/v/swarmauri_storage_s3_over_sftp?label=swarmauri_storage_s3_over_sftp&color=green" alt="Release Version"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a>
</p>

# Swarmauri Storage S3 Over SFTP

S3-style object storage adapter that persists bucket-prefixed objects through SFTP.

## Features

- Exposes Swarmauri storage adapter methods with S3-like `bucket/key` addressing over an SFTP directory tree.
- Supports password, key-file, and injected Paramiko transport or SFTP clients for managed connection lifecycles.
- Provides upload, download, recursive push and pull, byte-range reads, deletion, and bucket directory creation.
- Uses Swarmauri storage-key normalization helpers to reject unsafe keys before resolving remote or local paths.
- Provides discoverable `swarmauri.storage_adapters` and `peagen.plugins.storage_adapters` entry points.

## Installation

Install this package with `uv` or `pip`.

```bash
uv add swarmauri_storage_s3_over_sftp
```

```bash
pip install swarmauri_storage_s3_over_sftp
```

## Usage

Use this adapter when a workflow expects object-storage semantics but the backing system is reachable only through SFTP.

```python
from swarmauri_storage_s3_over_sftp import S3OverSftpStorageAdapter

adapter = S3OverSftpStorageAdapter.from_uri(
    "s3+sftp://deploy@example.com/artifacts/runs?root_dir=/srv/object-store"
)

uri = adapter.put_blob("latest/result.json", b'{"status":"ok"}')
payload = adapter.get_blob("latest/result.json")

print(uri)
print(payload)
```

The URI path is interpreted as `/<bucket>/<prefix>`. The optional `root_dir` query value points at the remote SFTP directory under which bucket directories are stored.

License: Apache-2.0. See `LICENSE`.
