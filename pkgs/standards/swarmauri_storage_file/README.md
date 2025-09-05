# Swarmauri File Storage Adapter

Filesystem-based storage adapter for Peagen that stores artifacts on the local disk.

## Installation

```bash
# pip install swarmauri_storage_file (when published)
```

## Usage

```python
from swarmauri_storage_file import FileStorageAdapter
import io

adapter = FileStorageAdapter(output_dir="/tmp/peagen")
uri = adapter.upload("example.txt", io.BytesIO(b"hello"))
print("Stored at", uri)
```
