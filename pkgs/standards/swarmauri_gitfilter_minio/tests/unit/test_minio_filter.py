import pytest

from swarmauri_gitfilter_minio import MinioFilter


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
    def __init__(self, *a, **k):
        self.store = {}

    def bucket_exists(self, bucket):
        return True

    def make_bucket(self, bucket):
        pass

    def get_object(self, bucket, key):
        if key not in self.store:
            raise FileNotFoundError(key)
        return DummyObject(self.store[key])

    def put_object(self, bucket, key, data, length=-1, part_size=0):
        self.store[key] = data.read()

    def list_objects(self, *a, **k):
        return []


@pytest.fixture
def filt(monkeypatch):
    monkeypatch.setattr(
        "swarmauri_gitfilter_minio.minio_filter.Minio",
        DummyClient,
    )
    return MinioFilter(
        endpoint="example.com",
        bucket="b",
        access_key="a",
        secret_key="s",
    )


def test_resource_type_serialization(filt):
    assert filt.resource == "StorageAdapter"
    assert filt.type == "MinioFilter"
    data = filt.model_dump()
    restored = MinioFilter(
        endpoint="example.com",
        bucket="b",
        access_key="a",
        secret_key="s",
        **data,
    )
    assert restored.type == filt.type


def test_clean_smudge(filt):
    oid = filt.clean(b"data")
    assert filt.smudge(oid) == b"data"
