# Swarmauri GitHub Release Storage Adapter

Stores artifacts as assets on a GitHub release for use with Peagen.

## Installation

```bash
# pip install swarmauri_storage_github_release (when published)
```

## Usage

```python
from swarmauri_storage_github_release import GithubReleaseStorageAdapter
from pydantic import SecretStr
import io

adapter = GithubReleaseStorageAdapter(
    token=SecretStr("ghp_..."),
    org="my-org",
    repo="my-repo",
    tag="v1.0.0",
)
uri = adapter.upload("artifact.txt", io.BytesIO(b"data"))
print(uri)
```
