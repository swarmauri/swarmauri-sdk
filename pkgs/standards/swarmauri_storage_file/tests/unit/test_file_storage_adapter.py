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
