from io import BytesIO

from swarmauri_storage_github import GithubStorageAdapter


adapter = GithubStorageAdapter()

# The adapter only inspects the key, so any binary stream is acceptable.
payload = BytesIO(
    b"# Example README\nThis payload would be uploaded to GitHub."
)
uri = adapter.upload("my-org/my-repo/README.md", payload)

print(uri)  # github://my-org/my-repo/README.md
