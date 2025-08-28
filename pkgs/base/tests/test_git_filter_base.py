from __future__ import annotations

from io import BytesIO

from swarmauri_base import GitFilterBase


class _DummyFilter(GitFilterBase):
    def __init__(self) -> None:
        self._store: dict[str, bytes] = {}

    @classmethod
    def from_uri(cls, uri: str) -> "_DummyFilter":
        return cls()

    def upload(self, key: str, data: BytesIO) -> str:  # type: ignore[override]
        self._store[key] = data.read()
        return key

    def download(self, key: str) -> BytesIO:  # type: ignore[override]
        return BytesIO(self._store[key])


def test_clean_smudge_roundtrip() -> None:
    filt = _DummyFilter.from_uri("dummy://")
    oid = filt.clean(b"data")
    assert filt.smudge(oid) == b"data"
