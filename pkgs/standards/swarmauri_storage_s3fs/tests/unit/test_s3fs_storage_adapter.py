import io
import mmap
from pathlib import Path
import tomllib

import pytest

from swarmauri_storage_s3fs import S3FSStorageAdapter


class DummyFile(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()


class DummyS3FS:
    instances = []

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.store = {}
        self.buckets = set()
        DummyS3FS.instances.append(self)

    def open(self, path, mode="rb"):
        if "r" in mode:
            if path not in self.store:
                raise FileNotFoundError(path)
            return DummyFile(self.store[path])

        fs = self

        class Writer(DummyFile):
            def close(self):
                fs.store[path] = self.getvalue()
                super().close()

        return Writer()

    def find(self, base):
        return sorted(path for path in self.store if path.startswith(base))

    def exists(self, path):
        return path in self.store or path in self.buckets

    def mkdir(self, path):
        self.buckets.add(path)

    def info(self, path):
        if path not in self.store:
            raise FileNotFoundError(path)
        return {"size": len(self.store[path])}

    def rm(self, path):
        self.store.pop(path, None)


@pytest.fixture
def adapter(monkeypatch):
    DummyS3FS.instances.clear()
    monkeypatch.setattr(
        "swarmauri_storage_s3fs.s3fs_storage_adapter.s3fs.S3FileSystem",
        DummyS3FS,
    )
    return S3FSStorageAdapter(
        bucket="bucket",
        prefix="runs",
        key="key",
        secret="secret",
        token="token",
        endpoint_url="https://example.test",
        region_name="us-test-1",
        use_ssl=False,
        client_kwargs={"addressing_style": "path"},
        config_kwargs={"signature_version": "s3v4"},
    )


def test_resource_type_serialization(adapter):
    assert adapter.resource == "StorageAdapter"
    assert adapter.type == "S3FSStorageAdapter"
    data = adapter.model_dump()
    restored = S3FSStorageAdapter(bucket="bucket", **data)
    assert restored.type == adapter.type


def test_constructor_passes_s3fs_options(adapter):
    kwargs = DummyS3FS.instances[0].kwargs
    assert kwargs["key"] == "key"
    assert kwargs["secret"] == "secret"
    assert kwargs["token"] == "token"
    assert kwargs["endpoint_url"] == "https://example.test"
    assert kwargs["use_ssl"] is False
    assert kwargs["client_kwargs"]["endpoint_url"] == "https://example.test"
    assert kwargs["client_kwargs"]["region_name"] == "us-test-1"
    assert kwargs["config_kwargs"] == {"signature_version": "s3v4"}


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
    assert DummyS3FS.instances[0].exists("bucket")

    adapter.upload("foo.txt", io.BytesIO(b"hello"))
    await adapter.remove_object("foo.txt")

    with pytest.raises(FileNotFoundError):
        adapter.download("foo.txt")


@pytest.mark.asyncio
async def test_get_range(adapter):
    adapter.upload("foo.txt", io.BytesIO(b"abcdef"))

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
    DummyS3FS.instances[0].store["bucket/runs/safe/../escaped.txt"] = b"owned"
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
        with mmap.mmap(
            file_handle.fileno(), 0, access=mmap.ACCESS_READ
        ) as source:
            adapter.upload_mmap("mmap.bin", source)

    with adapter.open_mmap("mmap.bin") as mapped:
        assert mapped.read() == b"mmap-content"


def test_from_uri(monkeypatch):
    monkeypatch.setattr(
        "swarmauri_storage_s3fs.s3fs_storage_adapter.s3fs.S3FileSystem",
        DummyS3FS,
    )

    adapter = S3FSStorageAdapter.from_uri("s3://demo-bucket/models")

    assert adapter.root_uri == "s3://demo-bucket/models/"


def test_storage_entry_points_declared():
    data = tomllib.loads(Path("pyproject.toml").read_text())

    assert (
        data["project"]["entry-points"]["swarmauri.storage_adapters"][
            "S3FSStorageAdapter"
        ]
        == "swarmauri_storage_s3fs.s3fs_storage_adapter:S3FSStorageAdapter"
    )
    assert (
        data["project"]["entry-points"]["peagen.plugins.storage_adapters"][
            "s3fs"
        ]
        == "swarmauri_storage_s3fs.s3fs_storage_adapter:S3FSStorageAdapter"
    )


def test_s3fs_adapter_does_not_import_other_s3_backends():
    source = Path(
        "swarmauri_storage_s3fs/s3fs_storage_adapter.py",
    ).read_text()

    assert "import s3fs" in source
    assert "import boto3" not in source
    assert "import botocore" not in source
    assert "import minio" not in source
