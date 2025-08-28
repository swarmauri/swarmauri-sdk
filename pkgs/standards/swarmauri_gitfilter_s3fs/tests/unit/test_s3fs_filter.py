import io

import pytest

from swarmauri_gitfilter_s3fs import S3FSFilter


class DummyFS:
    def __init__(self):
        self.store: dict[str, bytes] = {}

    def open(self, path, mode):
        if "w" in mode:
            fs = self

            class _Buf(io.BytesIO):
                def close(self_nonlocal):
                    fs.store[path] = self_nonlocal.getvalue()
                    super().close()

            return _Buf()
        if path not in self.store:
            raise FileNotFoundError(path)
        return io.BytesIO(self.store[path])

    def find(self, base):
        return list(self.store.keys())


@pytest.fixture
def filt(monkeypatch):
    monkeypatch.setattr(
        "swarmauri_gitfilter_s3fs.s3fs_filter.s3fs.S3FileSystem",
        lambda *a, **k: DummyFS(),
    )
    return S3FSFilter.from_uri("s3://bucket")


def test_resource_type_serialization(filt):
    assert filt.resource == "StorageAdapter"
    assert filt.type == "S3FSFilter"
    data = filt.model_dump()
    restored = S3FSFilter(bucket="bucket", **data)
    assert restored.type == filt.type


def test_clean_smudge(filt):
    oid = filt.clean(b"data")
    assert filt.smudge(oid) == b"data"
