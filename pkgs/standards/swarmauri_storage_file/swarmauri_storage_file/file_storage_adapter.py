"""Filesystem-based storage adapter.

Files are written to ``${root_dir}/${key}`` and directories are created
automatically.
"""

from __future__ import annotations

import io
import os
import shutil
from pathlib import Path
from typing import BinaryIO

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.storage import StorageAdapterBase


@ComponentBase.register_type(StorageAdapterBase, "FileStorageAdapter")
class FileStorageAdapter(StorageAdapterBase):
    """Write and read artefacts on the local disk."""

    def __init__(self, output_dir: str | os.PathLike, *, prefix: str = "", **kwargs):
        super().__init__(**kwargs)
        self._root = Path(output_dir).expanduser().resolve()
        self._root.mkdir(parents=True, exist_ok=True)
        self._prefix = prefix.lstrip("/")

    def _full_key(self, key: str) -> Path:
        key = key.lstrip("/")
        if self._prefix:
            return self._root / self._prefix / key
        return self._root / key

    @property
    def root_uri(self) -> str:
        """Return the workspace root as a ``file://`` URI."""
        base = f"file://{self._root.as_posix()}"
        return f"{base}/{self._prefix}" if self._prefix else f"{base}/"

    # ---------------------------------------------------------------- upload
    def upload(self, key: str, data: BinaryIO) -> str:
        """Copy *data* to ``${root_dir}/${key}`` atomically and return the artifact URI."""
        dest = self._full_key(key)
        dest.parent.mkdir(parents=True, exist_ok=True)

        tmp = dest.with_suffix(dest.suffix + ".tmp")
        with open(tmp, "wb") as fh:
            shutil.copyfileobj(data, fh)

        tmp.replace(dest)

        return f"{self.root_uri}{key.lstrip('/')}"

    # ---------------------------------------------------------------- download
    def download(self, key: str) -> BinaryIO:
        """Return a :class:`BytesIO` with the contents of ``${root_dir}/${key}``."""
        path = self._full_key(key)
        if not path.exists():
            raise FileNotFoundError(path)

        buffer = io.BytesIO(path.read_bytes())
        buffer.seek(0)
        return buffer

    # ---------------------------------------------------------------- upload_dir
    def upload_dir(self, src: str | os.PathLike, *, prefix: str = "") -> None:
        """Recursively upload files from *src* under ``prefix``."""
        base = Path(src)
        for path in base.rglob("*"):
            if path.is_file():
                rel = path.relative_to(base)
                key = os.path.join(prefix, rel.as_posix())
                with path.open("rb") as fh:
                    self.upload(key, fh)

    # ---------------------------------------------------------------- iter_prefix
    def iter_prefix(self, prefix: str):
        """Yield stored keys beginning with ``prefix``."""
        base = self._full_key(prefix)
        if not base.exists():
            return
        for path in base.rglob("*"):
            if path.is_file():
                rel = path.relative_to(self._root)
                yield str(rel)

    # ---------------------------------------------------------------- download_dir
    def download_dir(self, prefix: str, dest_dir: str | os.PathLike) -> None:
        """Copy all files under ``prefix`` into ``dest_dir``."""
        src_root = self._full_key(prefix)
        dest = Path(dest_dir)
        if not src_root.exists():
            return
        for path in src_root.rglob("*"):
            if path.is_file():
                rel = path.relative_to(src_root)
                target = dest / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, target)

    @classmethod
    def from_uri(cls, uri: str) -> "FileStorageAdapter":
        """Instantiate the adapter from a ``file://`` URI."""
        path = Path(uri[7:]).resolve()
        return cls(output_dir=path)
