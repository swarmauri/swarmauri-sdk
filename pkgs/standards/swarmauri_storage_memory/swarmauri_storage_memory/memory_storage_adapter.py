"""In-memory storage adapter."""

from __future__ import annotations

import io
import os
from pathlib import Path
from typing import BinaryIO, Iterable

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.storage import StorageAdapterBase


@ComponentBase.register_type(StorageAdapterBase, "MemoryStorageAdapter")
class MemoryStorageAdapter(StorageAdapterBase):
    """Store and retrieve artifacts entirely in memory."""

    def __init__(self, *, prefix: str = "", **kwargs) -> None:
        super().__init__(**kwargs)
        self._prefix = prefix.lstrip("/")
        self._store: dict[str, bytes] = {}

    def _full_key(self, key: str) -> str:
        key = key.lstrip("/")
        if self._prefix:
            return f"{self._prefix}/{key}" if key else self._prefix
        return key

    @property
    def root_uri(self) -> str:
        """Return the root memory URI for this adapter."""
        if self._prefix:
            return f"memory://{self._prefix}/"
        return "memory://"

    def upload(self, key: str, data: BinaryIO) -> str:
        """Store *data* in memory and return the artifact URI."""
        full_key = self._full_key(key)
        self._store[full_key] = data.read()
        return f"{self.root_uri}{key.lstrip('/')}"

    def download(self, key: str) -> BinaryIO:
        """Return a :class:`BytesIO` with the stored contents."""
        full_key = self._full_key(key)
        if full_key not in self._store:
            raise FileNotFoundError(full_key)
        buffer = io.BytesIO(self._store[full_key])
        buffer.seek(0)
        return buffer

    def upload_dir(self, src: str | os.PathLike, *, prefix: str = "") -> None:
        """Recursively upload files from *src* under ``prefix``."""
        base = Path(src)
        for path in base.rglob("*"):
            if path.is_file():
                rel = path.relative_to(base)
                key = os.path.join(prefix, rel.as_posix())
                with path.open("rb") as fh:
                    self.upload(key, fh)

    def iter_prefix(self, prefix: str) -> Iterable[str]:
        """Yield stored keys beginning with ``prefix``."""
        base = self._full_key(prefix).rstrip("/")
        for key in sorted(self._store):
            if not base or key == base or key.startswith(f"{base}/"):
                yield key

    def download_dir(self, prefix: str, dest_dir: str | os.PathLike) -> None:
        """Copy all stored artifacts under ``prefix`` into ``dest_dir``."""
        base = self._full_key(prefix).rstrip("/")
        dest_root = Path(dest_dir)
        for key, payload in self._store.items():
            if base and not (key == base or key.startswith(f"{base}/")):
                continue
            rel = key[len(base) :].lstrip("/") if base else key
            if not rel:
                continue
            target = dest_root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)

    @classmethod
    def from_uri(cls, uri: str) -> "MemoryStorageAdapter":
        """Instantiate the adapter from a ``memory://`` URI."""
        prefix = uri.removeprefix("memory://").strip("/")
        return cls(prefix=prefix)
