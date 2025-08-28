# Swarmauri GitHub Storage Adapter

Simplified storage adapter for Peagen that records uploads as `github://` URIs.

## Installation

```bash
# pip install swarmauri_storage_github (when published)
```

## Usage

```python
from swarmauri_storage_github import GithubStorageAdapter

adapter = GithubStorageAdapter()
uri = adapter.upload("README.md", "my-org/my-repo/README.md")
print(uri)
```
