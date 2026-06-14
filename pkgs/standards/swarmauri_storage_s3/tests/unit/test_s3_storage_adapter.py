import io
import mmap
from pathlib import Path
import tomllib

import pytest
from botocore.exceptions import ClientError

from swarmauri_storage_s3 import S3StorageAdapter


class DummyBody(io.BytesIO):
    pass


class DummyClient:
    instances = []

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.store = {}
        self.buckets = set()
        DummyClient.instances.append(self)

    def upload_fileobj(self, data, bucket, key):
        self.store[(bucket, key)] = data.read()

    def download_fileobj(self, bucket, key, fileobj):
        try:
            fileobj.write(self.store[(bucket, key)])
        except KeyError as exc:
            raise self._missing("NoSuchKey") from exc

    def put_object(self, Bucket, Key, Body, ContentType=None):
        del ContentType
        self.store[(Bucket, Key)] = Body

    def get_object(self, Bucket, Key, Range=None):
        try:
            payload = self.store[(Bucket, Key)]
        except KeyError as exc:
            raise self._missing("NoSuchKey") from exc
        if Range:
            bounds = Range.removeprefix("bytes=").split("-")
            start = int(bounds[0])
            end = int(bounds[1])
            payload = payload[start : end + 1]
        return {"Body": DummyBody(payload)}

    def head_object(self, Bucket, Key):
        try:
            return {"ContentLength": len(self.store[(Bucket, Key)])}
        except KeyError as exc:
            raise self._missing("NoSuchKey") from exc

    def list_objects_v2(self, Bucket, Prefix="", ContinuationToken=None):
        del ContinuationToken
        contents = [
            {"Key": key}
            for bucket, key in sorted(self.store)
            if bucket == Bucket and key.startswith(Prefix)
        ]
        return {"Contents": contents, "IsTruncated": False}

    def head_bucket(self, Bucket):
        if Bucket not in self.buckets:
            raise self._missing("NoSuchBucket")

    def create_bucket(self, Bucket):
        self.buckets.add(Bucket)

    def delete_object(self, Bucket, Key):
        self.store.pop((Bucket, Key), None)

    @staticmethod
    def _missing(code):
        return ClientError({"Error": {"Code": code}}, "test")


def _fake_client(**kwargs):
    return DummyClient(**kwargs)


@pytest.fixture
def adapter(monkeypatch):
    DummyClient.instances.clear()
    monkeypatch.setattr(
        "swarmauri_storage_s3.s3_storage_adapter.boto3.client", _fake_client
    )
    return S3StorageAdapter(
        bucket="bucket",
        prefix="runs",
        endpoint_url="https://example.test",
        region_name="us-test-1",
        access_key="key",
        secret_key="secret",
        session_token="token",
        use_ssl=False,
        verify=False,
        addressing_style="path",
        client_kwargs={"api_version": "2006-03-01"},
        config_kwargs={"signature_version": "s3v4"},
    )


def test_resource_type_serialization(adapter, monkeypatch):
    monkeypatch.setattr(
        "swarmauri_storage_s3.s3_storage_adapter.boto3.client", _fake_client
    )

    assert adapter.resource == "StorageAdapter"
    assert adapter.type == "S3StorageAdapter"
    data = adapter.model_dump()
    restored = S3StorageAdapter(bucket="bucket", **data)
    assert restored.type == adapter.type


def test_constructor_passes_generic_s3_client_options(adapter):
    kwargs = DummyClient.instances[0].kwargs
    assert kwargs["service_name"] == "s3"
    assert kwargs["endpoint_url"] == "https://example.test"
    assert kwargs["region_name"] == "us-test-1"
    assert kwargs["aws_access_key_id"] == "key"
    assert kwargs["aws_secret_access_key"] == "secret"
    assert kwargs["aws_session_token"] == "token"
    assert kwargs["use_ssl"] is False
    assert kwargs["verify"] is False
    assert kwargs["api_version"] == "2006-03-01"
    assert kwargs["config"].s3["addressing_style"] == "path"


def test_upload_download_and_iter_prefix(adapter):
    uri = adapter.upload("out/foo.txt", io.BytesIO(b"hello"))

    assert uri == "s3://bucket/runs/out/foo.txt"
    assert adapter.download("out/foo.txt").read() == b"hello"
    assert list(adapter.iter_prefix("out")) == ["out/foo.txt"]


def test_missing_download_raises_file_not_found(adapter):
    with pytest.raises(FileNotFoundError):
        adapter.download("missing.txt")


@pytest.mark.asyncio
async def test_ensure_bucket_and_remove(adapter):
    await adapter.ensure_bucket()
    assert "bucket" in DummyClient.instances[0].buckets

    adapter.upload("foo.txt", io.BytesIO(b"hello"))
    await adapter.remove_object("foo.txt")

    with pytest.raises(FileNotFoundError):
        adapter.download("foo.txt")


@pytest.mark.asyncio
async def test_put_get_bytes_and_range(adapter):
    await adapter.put_bytes("foo.txt", b"abcdef", "text/plain")

    assert await adapter.get_bytes("foo.txt") == b"abcdef"
    assert await adapter.get_range("foo.txt", 2, 3) == b"cde"


def test_push_pull(adapter, tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "nested.txt").write_bytes(b"payload")

    adapter.push(src, prefix="prefix")

    dest = tmp_path / "dest"
    adapter.pull("prefix", dest)

    assert (dest / "nested.txt").read_bytes() == b"payload"


def test_pull_rejects_path_traversal_object_key(adapter, tmp_path):
    DummyClient.instances[0].store[("bucket", "runs/safe/../escaped.txt")] = b"owned"
    dest = tmp_path / "dest"
    outside = tmp_path / "escaped.txt"

    with pytest.raises(ValueError, match="unsafe storage key"):
        adapter.pull("safe", dest)

    assert not outside.exists()


def test_upload_memoryview_and_mmap(adapter, tmp_path):
    adapter.upload_memoryview("memory.bin", memoryview(b"payload"))
    assert adapter.download_memoryview("memory.bin").tobytes() == b"payload"

    path = tmp_path / "blob.bin"
    path.write_bytes(b"mmap-content")
    with path.open("r+b") as file_handle:
        with mmap.mmap(file_handle.fileno(), 0, access=mmap.ACCESS_READ) as source:
            adapter.upload_mmap("mmap.bin", source)

    with adapter.open_mmap("mmap.bin") as mapped:
        assert mapped.read() == b"mmap-content"


def test_from_uri(monkeypatch):
    monkeypatch.setattr(
        "swarmauri_storage_s3.s3_storage_adapter.boto3.client", _fake_client
    )

    adapter = S3StorageAdapter.from_uri("s3://demo-bucket/models")

    assert adapter.root_uri == "s3://demo-bucket/models/"


def test_storage_entry_points_declared():
    data = tomllib.loads(Path("pyproject.toml").read_text())

    assert (
        data["project"]["entry-points"]["swarmauri.storage_adapters"][
            "S3StorageAdapter"
        ]
        == "swarmauri_storage_s3.s3_storage_adapter:S3StorageAdapter"
    )
    assert (
        data["project"]["entry-points"]["peagen.plugins.storage_adapters"]["s3"]
        == "swarmauri_storage_s3.s3_storage_adapter:S3StorageAdapter"
    )
