import io
from pathlib import Path

import pytest

from peagen.storage_adapters.file_storage_adapter import FileStorageAdapter
from peagen.storage_adapters.github_storage_adapter import GithubStorageAdapter
from peagen.storage_adapters.gh_release_storage_adapter import GithubReleaseStorageAdapter
from peagen.storage_adapters import minio_storage_adapter
from peagen.storage_adapters.minio_storage_adapter import MinioStorageAdapter


@pytest.mark.unit
def test_file_storage_adapter_basic(tmp_path: Path):
    adapter = FileStorageAdapter(tmp_path)
    data = b"hello"
    uri = adapter.upload("foo.txt", io.BytesIO(data))
    assert uri == f"file://{tmp_path.as_posix()}/foo.txt"
    out = adapter.download("foo.txt").read()
    assert out == data


@pytest.mark.unit
def test_file_storage_adapter_prefix_ops(tmp_path: Path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.txt").write_text("A")
    (src / "sub").mkdir()
    (src / "sub" / "b.txt").write_text("B")

    adapter = FileStorageAdapter(tmp_path, prefix="pfx")
    adapter.upload_dir(src)

    keys = set(adapter.iter_prefix(""))
    assert keys == {"pfx/a.txt", "pfx/sub/b.txt"}

    dest = tmp_path / "dest"
    adapter.download_prefix("", dest)
    assert (dest / "a.txt").read_text() == "A"
    assert (dest / "sub" / "b.txt").read_text() == "B"
    assert adapter.root_uri == f"file://{tmp_path.as_posix()}/pfx"


@pytest.mark.unit
def test_github_storage_adapter_upload():
    adapter = GithubStorageAdapter(token="x")
    assert adapter.upload("src", "dest/path") == "github://dest/path"


class DummyS3Error(Exception):
    pass


class DummyMinio:
    def __init__(self, endpoint, access_key=None, secret_key=None, secure=True):
        self.endpoint = endpoint
        self.secure = secure
        self.buckets = set()
        self.objects = {}

    def bucket_exists(self, bucket):
        return bucket in self.buckets

    def make_bucket(self, bucket):
        self.buckets.add(bucket)

    def put_object(self, bucket, key, data, length=-1, part_size=10 * 1024 * 1024):
        self.objects[(bucket, key)] = data.read()

    class _Resp:
        def __init__(self, data):
            self._data = data

        def read(self):
            return self._data

        def close(self):
            pass

        def release_conn(self):
            pass

    def get_object(self, bucket, key):
        if (bucket, key) not in self.objects:
            raise DummyS3Error
        return self._Resp(self.objects[(bucket, key)])

    def list_objects(self, bucket, prefix="", recursive=True):
        for (b, k), _ in self.objects.items():
            if b == bucket and k.startswith(prefix):
                yield type("Obj", (), {"object_name": k})()


@pytest.mark.unit
def test_minio_storage_adapter_ops(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(minio_storage_adapter, "Minio", DummyMinio)
    monkeypatch.setattr(minio_storage_adapter, "S3Error", DummyS3Error)
    monkeypatch.setattr(minio_storage_adapter, "load_peagen_toml", lambda: {"storage": {"adapters": {"minio": {"access_key": "ak", "secret_key": "sk"}}}})

    adapter = MinioStorageAdapter.from_uri("minio://host:9000/bkt/pfx")
    assert adapter.root_uri == "minio://host:9000/bkt/pfx/"

    uri = adapter.upload("foo.txt", io.BytesIO(b"hi"))
    assert uri == "minio://host:9000/bkt/pfx/foo.txt"
    assert adapter.download("foo.txt").read() == b"hi"

    keys = list(adapter.iter_prefix(""))
    assert keys == ["foo.txt"]

    dest = tmp_path / "dest"
    adapter.download_prefix("", dest)
    assert (dest / "foo.txt").read_bytes() == b"hi"


class DummyAsset:
    def __init__(self, release, name):
        self.release = release
        self.name = name
        self.url = f"http://dummy/{name}"

    def delete_asset(self):
        del self.release.assets[self.name]


class DummyRelease:
    def __init__(self):
        self.assets = {}

    def get_assets(self):
        return [DummyAsset(self, name) for name in list(self.assets.keys())]

    def upload_asset(self, path, name, label):
        with open(path, "rb") as fh:
            self.assets[name] = fh.read()


class DummyRequester:
    def __init__(self, release):
        self.release = release

    def requestBytes(self, method, url, headers=None):
        name = url.split("dummy/")[-1]
        return None, self.release.assets[name]


class DummyClient:
    def __init__(self, release):
        self._Github__requester = DummyRequester(release)


def fake_init(self, token, org, repo, tag, *, release_name=None, message="", draft=False, prerelease=False, prefix=""):
    self._release = DummyRelease()
    self._client = DummyClient(self._release)
    self._repo = type("Repo", (), {"full_name": f"{org}/{repo}"})()
    self._tag = tag
    self._prefix = prefix.lstrip("/")


@pytest.mark.unit
def test_github_release_storage_adapter_ops(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(
        GithubReleaseStorageAdapter,
        "__init__",
        fake_init,
        raising=False,
    )
    monkeypatch.setattr(
        "peagen.storage_adapters.gh_release_storage_adapter.load_peagen_toml",
        lambda: {"storage": {"adapters": {"gh_release": {"token": "tok"}}}},
    )

    adapter = GithubReleaseStorageAdapter.from_uri("ghrel://ORG/REPO/v1/pfx")
    assert adapter.root_uri == "ghrel://ORG/REPO/v1/pfx/"

    uri = adapter.upload("a.txt", io.BytesIO(b"data"))
    assert uri == "ghrel://ORG/REPO/v1/pfx/pfx/a.txt"
    assert adapter.download("a.txt").read() == b"data"

    assert list(adapter.iter_prefix("")) == ["a.txt"]

    dest = tmp_path / "dest"
    adapter.download_prefix("", dest)
    assert (dest / "a.txt").read_bytes() == b"data"
