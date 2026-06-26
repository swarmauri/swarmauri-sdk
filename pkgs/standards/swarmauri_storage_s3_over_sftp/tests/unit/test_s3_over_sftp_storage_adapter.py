import errno
import io
import mmap
from pathlib import Path
import stat
import tomllib

import pytest

from swarmauri_storage_s3_over_sftp import S3OverSftpStorageAdapter


class Attr:
    def __init__(self, filename, st_mode, st_size=0):
        self.filename = filename
        self.st_mode = st_mode
        self.st_size = st_size


class DummySftp:
    def __init__(self):
        self.files = {}
        self.dirs = {"/", "/remote", "/remote/root"}
        self.closed = False

    def close(self):
        self.closed = True

    def _norm(self, path):
        return "/" + path.strip("/")

    def stat(self, path):
        path = self._norm(path)
        if path in self.dirs:
            return Attr(Path(path).name, stat.S_IFDIR)
        if path in self.files:
            return Attr(Path(path).name, stat.S_IFREG, len(self.files[path]))
        raise FileNotFoundError(errno.ENOENT, "No such file")

    def mkdir(self, path):
        self.dirs.add(self._norm(path))

    def open(self, path, mode):
        path = self._norm(path)
        if "w" in mode:
            return WritableRemote(self, path)
        if path not in self.files:
            raise FileNotFoundError(errno.ENOENT, "No such file")
        return io.BytesIO(self.files[path])

    def remove(self, path):
        self.files.pop(self._norm(path), None)

    def listdir_attr(self, path):
        path = self._norm(path)
        if path not in self.dirs:
            raise FileNotFoundError(errno.ENOENT, "No such file")
        prefix = path.rstrip("/") + "/"
        names = set()
        for directory in self.dirs:
            if directory.startswith(prefix):
                remainder = directory[len(prefix) :]
                if remainder:
                    names.add((remainder.split("/", 1)[0], True))
        for filename in self.files:
            if filename.startswith(prefix):
                remainder = filename[len(prefix) :]
                if remainder:
                    names.add((remainder.split("/", 1)[0], False))
        attrs = []
        for name, is_dir in sorted(names):
            child = prefix + name
            if is_dir and child in self.dirs:
                attrs.append(Attr(name, stat.S_IFDIR))
            elif not is_dir:
                attrs.append(Attr(name, stat.S_IFREG, len(self.files[child])))
        return attrs


class WritableRemote(io.BytesIO):
    def __init__(self, sftp, path):
        super().__init__()
        self._sftp = sftp
        self._path = path

    def close(self):
        self._sftp.files[self._path] = self.getvalue()
        super().close()


@pytest.fixture
def sftp():
    return DummySftp()


@pytest.fixture
def adapter(sftp):
    return S3OverSftpStorageAdapter(
        bucket="bucket",
        prefix="runs",
        host="example.test",
        username="deploy",
        root_dir="/remote/root",
        sftp_client=sftp,
    )


def test_resource_type_serialization(adapter, sftp):
    assert adapter.resource == "StorageAdapter"
    assert adapter.type == "S3OverSftpStorageAdapter"
    data = adapter.model_dump()
    restored = S3OverSftpStorageAdapter(
        bucket="bucket", sftp_client=sftp, **data
    )
    assert restored.type == adapter.type


def test_upload_download_and_iter_prefix(adapter):
    uri = adapter.upload("out/foo.txt", io.BytesIO(b"hello"))

    assert uri == "s3+sftp://deploy@example.test/bucket/runs/out/foo.txt"
    assert adapter.download("out/foo.txt").read() == b"hello"
    assert list(adapter.iter_prefix("out")) == ["out/foo.txt"]


def test_missing_download_raises_file_not_found(adapter):
    with pytest.raises(FileNotFoundError):
        adapter.download("missing.txt")


@pytest.mark.asyncio
async def test_ensure_bucket_put_get_range_and_remove(adapter, sftp):
    await adapter.ensure_bucket()
    assert "/remote/root/bucket" in sftp.dirs

    await adapter.put_bytes("foo.txt", b"abcdef", "text/plain")
    assert await adapter.get_bytes("foo.txt") == b"abcdef"
    assert await adapter.get_range("foo.txt", 2, 3) == b"cde"

    await adapter.remove_object("foo.txt")
    with pytest.raises(FileNotFoundError):
        adapter.download("foo.txt")


def test_push_pull(adapter, tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "nested.txt").write_bytes(b"payload")

    adapter.push(src, prefix="prefix")

    dest = tmp_path / "dest"
    adapter.pull("prefix", dest)

    assert (dest / "nested.txt").read_bytes() == b"payload"


def test_pull_rejects_path_traversal_object_key(
    adapter, sftp, tmp_path, monkeypatch
):
    def hostile_listdir(path):
        assert path == "/remote/root/bucket/runs/safe"
        return [Attr("../escaped.txt", stat.S_IFREG, 5)]

    sftp.dirs.add("/remote/root/bucket/runs/safe")
    monkeypatch.setattr(sftp, "listdir_attr", hostile_listdir)
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


def test_from_uri(monkeypatch, sftp):
    class DummySshClient:
        instances = []

        def __init__(self):
            self.kwargs = None
            self.loaded_keys = False
            DummySshClient.instances.append(self)

        def load_system_host_keys(self):
            self.loaded_keys = True

        def connect(self, **kwargs):
            self.kwargs = kwargs

        def open_sftp(self):
            return sftp

        def close(self):
            pass

    monkeypatch.setattr(
        "swarmauri_storage_s3_over_sftp.s3_over_sftp_storage_adapter."
        "paramiko.SSHClient",
        DummySshClient,
    )

    adapter = S3OverSftpStorageAdapter.from_uri(
        "s3+sftp://deploy:secret@example.test:2222/demo-bucket/models"
        "?root_dir=/remote/root"
    )

    assert (
        adapter.root_uri
        == "s3+sftp://deploy@example.test:2222/demo-bucket/models/"
    )
    assert DummySshClient.instances[0].loaded_keys is True
    assert DummySshClient.instances[0].kwargs["hostname"] == "example.test"
    assert DummySshClient.instances[0].kwargs["port"] == 2222
    assert DummySshClient.instances[0].kwargs["username"] == "deploy"
    assert DummySshClient.instances[0].kwargs["password"] == "secret"


def test_storage_entry_points_declared():
    data = tomllib.loads(Path("pyproject.toml").read_text())

    assert (
        data["project"]["entry-points"]["swarmauri.storage_adapters"][
            "S3OverSftpStorageAdapter"
        ]
        == "swarmauri_storage_s3_over_sftp.s3_over_sftp_storage_adapter:"
        "S3OverSftpStorageAdapter"
    )
    assert (
        data["project"]["entry-points"]["peagen.plugins.storage_adapters"][
            "s3-over-sftp"
        ]
        == "swarmauri_storage_s3_over_sftp.s3_over_sftp_storage_adapter:"
        "S3OverSftpStorageAdapter"
    )
