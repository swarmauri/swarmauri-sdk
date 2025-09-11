import io


from swarmauri_storage_github import GithubStorageAdapter


def test_ubc_resource_type():
    adapter = GithubStorageAdapter()
    assert adapter.resource == "StorageAdapter"
    assert adapter.type == "GithubStorageAdapter"


def test_round_trip_serialization():
    adapter = GithubStorageAdapter()
    serialized = adapter.model_dump_json()
    restored = GithubStorageAdapter.model_validate_json(serialized)
    assert restored.type == adapter.type


def test_upload_returns_uri():
    adapter = GithubStorageAdapter()
    uri = adapter.upload("foo.txt", io.BytesIO(b"hi"))
    assert uri == "github://foo.txt"
