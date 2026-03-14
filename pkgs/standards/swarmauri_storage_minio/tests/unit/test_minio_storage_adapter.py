import io
import mmap

import pytest

from swarmauri_storage_minio import MinioStorageAdapter


class DummyObject:
    def __init__(self, data: bytes):
        self._data = data

    def read(self):
        return self._data

    def close(self):
        pass

    def release_conn(self):
        pass


class DummyClient:
    def __init__(self, *args, **kwargs):
        self.store = {}

    def bucket_exists(self, bucket):
        return True

    def make_bucket(self, bucket):
        pass

    def put_object(self, bucket, key, data, length=-1, part_size=0):
        self.store[key] = data.read()

    def get_object(self, bucket, key):
        if key not in self.store:
            raise Exception("not found")
        return DummyObject(self.store[key])

    def list_objects(self, bucket, prefix="", recursive=True):
        class Obj:
            def __init__(self, name):
                self.object_name = name

        for k in self.store.keys():
            if k.startswith(prefix):
                yield Obj(k)


@pytest.fixture
def adapter(monkeypatch):
    monkeypatch.setattr(
        "swarmauri_storage_minio.minio_storage_adapter.Minio",
        DummyClient,
    )
    return MinioStorageAdapter(
        endpoint="example.com",
        bucket="b",
        access_key="a",
        secret_key="s",
    )


def test_resource_type_serialization(adapter):
    assert adapter.resource == "StorageAdapter"
    assert adapter.type == "MinioStorageAdapter"
    data = adapter.model_dump()
    restored = MinioStorageAdapter(
        endpoint="example.com",
        bucket="b",
        access_key="a",
        secret_key="s",
        **data,
    )
    assert restored.type == adapter.type


def test_upload_download(adapter):
    uri = adapter.upload("foo.txt", io.BytesIO(b"hi"))
    assert uri.endswith("foo.txt")
    data = adapter.download("foo.txt").read()
    assert data == b"hi"


def test_upload_memoryview_and_download_memoryview(adapter):
    uri = adapter.upload_memoryview("memoryview.bin", memoryview(b"payload"))
    assert uri.endswith("memoryview.bin")

    result = adapter.download_memoryview("memoryview.bin")
    assert isinstance(result, memoryview)
    assert result.tobytes() == b"payload"


def test_upload_mmap_and_open_mmap(adapter, tmp_path):
    path = tmp_path / "blob.bin"
    path.write_bytes(b"mmap-content")

    with path.open("r+b") as file_handle:
        with mmap.mmap(file_handle.fileno(), 0, access=mmap.ACCESS_READ) as source:
            uri = adapter.upload_mmap("mmap.bin", source)

    assert uri.endswith("mmap.bin")
    with adapter.open_mmap("mmap.bin") as mapped:
        assert mapped.read() == b"mmap-content"


def test_open_mmap_rejects_empty_objects(adapter):
    adapter.upload("empty.bin", io.BytesIO(b""))

    with pytest.raises(ValueError, match="cannot create mmap"):
        with adapter.open_mmap("empty.bin"):
            pass


def test_put_get_blob(adapter):
    uri = adapter.put_blob("blob.txt", b"payload")
    assert uri.endswith("blob.txt")
    assert adapter.get_blob("blob.txt") == b"payload"


def test_push_pull(adapter, tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "nested.txt").write_bytes(b"hello")

    adapter.push(src, prefix="prefix")

    dest = tmp_path / "dest"
    adapter.pull("prefix", dest)

    assert (dest / "nested.txt").read_bytes() == b"hello"
