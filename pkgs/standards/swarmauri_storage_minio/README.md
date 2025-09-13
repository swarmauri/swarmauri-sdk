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

Peagen storage adapter that saves artifacts to a MinIO or S3-compatible bucket.

## Installation

```bash
# pip install swarmauri_storage_minio (when published)
```

## Usage

```python
from swarmauri_storage_minio import MinioStorageAdapter
from pydantic import SecretStr
import io

adapter = MinioStorageAdapter(
    endpoint="localhost:9000",
    access_key=SecretStr("minio"),
    secret_key=SecretStr("minio123"),
    bucket="peagen",
)
uri = adapter.upload("artifact.txt", io.BytesIO(b"data"))
print(uri)
```
