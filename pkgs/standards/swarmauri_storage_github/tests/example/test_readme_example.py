import io

import pytest

from swarmauri_storage_github import GithubStorageAdapter


@pytest.mark.example
def test_readme_quickstart_example() -> None:
    adapter = GithubStorageAdapter()
    payload = io.BytesIO(b"# Example README\nThis payload would be uploaded to GitHub.")

    uri = adapter.upload("my-org/my-repo/README.md", payload)

    assert uri == "github://my-org/my-repo/README.md"
