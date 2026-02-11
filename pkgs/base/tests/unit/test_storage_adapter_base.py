import io

from swarmauri_base.storage import StorageAdapterBase


class DummyStorageAdapter(StorageAdapterBase):
    def __init__(self):
        super().__init__()
        self._store: dict[str, bytes] = {}
        self.upload_dir_calls: list[tuple[str, str]] = []
        self.download_dir_calls: list[tuple[str, str]] = []

    def upload(self, key: str, data: io.BytesIO) -> str:
        self._store[key] = data.read()
        return f"dummy://{key}"

    def download(self, key: str) -> io.BytesIO:
        return io.BytesIO(self._store[key])

    def upload_dir(self, src: str, *, prefix: str = "") -> None:
        self.upload_dir_calls.append((src, prefix))

    def download_dir(self, prefix: str, dest_dir: str) -> None:
        self.download_dir_calls.append((prefix, dest_dir))

    @classmethod
    def from_uri(cls, uri: str) -> "DummyStorageAdapter":
        return cls()


def test_storage_adapter_base_blob_helpers():
    adapter = DummyStorageAdapter()
    uri = adapter.put_blob("demo.txt", b"payload")
    assert uri == "dummy://demo.txt"
    assert adapter.get_blob("demo.txt") == b"payload"


def test_storage_adapter_base_push_pull():
    adapter = DummyStorageAdapter()
    adapter.push("src", prefix="prefix")
    adapter.pull("prefix", "dest")
    assert adapter.upload_dir_calls == [("src", "prefix")]
    assert adapter.download_dir_calls == [("prefix", "dest")]
