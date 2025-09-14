import io

from swarmauri_base.git_filters import GitFilterBase


class DummyFilter(GitFilterBase):
    def __init__(self):
        self.store: dict[str, bytes] = {}

    def upload(self, key: str, data: io.BytesIO) -> str:  # type: ignore[override]
        self.store[key] = data.read()
        return key

    def download(self, key: str) -> io.BytesIO:  # type: ignore[override]
        return io.BytesIO(self.store[key])

    @classmethod
    def from_uri(cls, uri: str) -> "DummyFilter":  # pragma: no cover - simple
        return cls()


def test_clean_smudge_roundtrip():
    filt = DummyFilter()
    oid = filt.clean(b"data")
    assert filt.smudge(oid) == b"data"
