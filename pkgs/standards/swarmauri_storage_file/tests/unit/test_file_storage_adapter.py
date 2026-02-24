import io

import pytest

from swarmauri_storage_file import FileStorageAdapter


@pytest.fixture
def adapter(tmp_path):
    return FileStorageAdapter(output_dir=tmp_path)


def test_ubc_resource(adapter):
    assert adapter.resource == "StorageAdapter"


def test_ubc_type(adapter):
    assert adapter.type == "FileStorageAdapter"


def test_round_trip_serialization(adapter):
    data = adapter.model_dump()
    restored = FileStorageAdapter(output_dir=adapter._root, **data)
    assert restored.type == adapter.type


def test_upload_download(adapter):
    data = io.BytesIO(b"hello")
    uri = adapter.upload("foo.txt", data)
    assert uri.endswith("foo.txt")
    out = adapter.download("foo.txt").read()
    assert out == b"hello"


def test_put_get_blob(adapter):
    uri = adapter.put_blob("blob.txt", b"payload")
    assert uri.endswith("blob.txt")
    assert adapter.get_blob("blob.txt") == b"payload"


def test_push_pull(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "nested.txt").write_bytes(b"hello")

    adapter = FileStorageAdapter(output_dir=tmp_path / "store")
    adapter.push(src, prefix="prefix")

    dest = tmp_path / "dest"
    adapter.pull("prefix", dest)

    assert (dest / "nested.txt").read_bytes() == b"hello"
