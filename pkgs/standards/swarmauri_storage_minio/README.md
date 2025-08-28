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
