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


#class FileStorageAdapter(IStorageAdapter):
class FileStorageAdapter:
    """Write and read artefacts on the local disk."""

    def __init__(self, root_dir: str | os.PathLike):
        self._root = Path(root_dir).expanduser().resolve()
        self._root.mkdir(parents=True, exist_ok=True)

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

        tmp.replace(dest)   # atomic on POSIX

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
