"""
peagen/storage_adapters/file_storage_adapter.py
───────────────────────────────────────────────
Local-filesystem implementation of `IStorageAdapter`.

Key → `${root_dir}/${key}`  (directories are created automatically)
"""

from __future__ import annotations

import io
import os
import shutil
from pathlib import Path
from typing import BinaryIO

# from swarmauri_core.storage_adapters.IStorageAdapter import IStorageAdapter


# class FileStorageAdapter(IStorageAdapter):
class FileStorageAdapter:
    """Write and read artefacts on the local disk."""

    def __init__(self, output_dir: str | os.PathLike):
        self._root = Path(output_dir).expanduser().resolve()
        self._root.mkdir(parents=True, exist_ok=True)

    @property
    def root_uri(self) -> str:
        """
        Absolute on-disk location of the workspace, expressed as a URI that
        remote-aware code can still parse.
        Example:  file:///home/ci/artifacts/peagen_run_42/
        """
        return f"file://{self._root.as_posix()}/"

    # ---------------------------------------------------------------- upload
    def upload(self, key: str, data: BinaryIO) -> None:
        """
        Copy *data* to `${root_dir}/${key}` atomically.

        Large payloads are streamed in chunks; small BytesIO’s are copied at
        once.  Existing files are overwritten.
        """
        dest = self._root / key
        dest.parent.mkdir(parents=True, exist_ok=True)

        # Ensure restartable writes: write to tmp, then replace
        tmp = dest.with_suffix(dest.suffix + ".tmp")
        with open(tmp, "wb") as fh:
            shutil.copyfileobj(data, fh)

        tmp.replace(dest)  # atomic on POSIX

    # ---------------------------------------------------------------- download
    def download(self, key: str) -> BinaryIO:
        """
        Open `${root_dir}/${key}` and return a BytesIO so the caller gets a
        file-like object just like S3/MinIO download().
        """
        path = self._root / key
        if not path.exists():
            raise FileNotFoundError(path)

        buffer = io.BytesIO(path.read_bytes())
        buffer.seek(0)
        return buffer

    # ---------------------------------------------------------------- upload_dir
    def upload_dir(self, src: str | os.PathLike, *, prefix: str = "") -> None:
        """Recursively upload all files under *src* with keys prefixed by ``prefix``."""
        base = Path(src)
        for path in base.rglob("*"):
            if path.is_file():
                rel = path.relative_to(base)
                key = os.path.join(prefix, rel.as_posix())
                with path.open("rb") as fh:
                    self.upload(key, fh)

    # ---------------------------------------------------------------- iter_prefix
    def iter_prefix(self, prefix: str):
        """Yield stored keys starting with ``prefix``."""
        base = self._root / prefix
        if not base.exists():
            return
        for path in base.rglob("*"):
            if path.is_file():
                yield str(path.relative_to(self._root))

    # ---------------------------------------------------------------- download_prefix
    def download_prefix(self, prefix: str, dest_dir: str | os.PathLike) -> None:
        """Copy all files under ``prefix`` into ``dest_dir``."""
        src_root = self._root / prefix
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
        # file:///absolute/path/
        path = Path(uri[7:]).resolve()
        return cls(output_dir=path)