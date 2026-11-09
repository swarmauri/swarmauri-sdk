from __future__ import annotations

from pathlib import Path
import io
import os
from typing import BinaryIO

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.storage import StorageAdapterBase
from swarmauri_base.git_filters import GitFilterBase
from swarmauri_storage_file import FileStorageAdapter


@ComponentBase.register_type(StorageAdapterBase, "FileFilter")
class FileFilter(FileStorageAdapter, GitFilterBase):
    """Git filter that stores files on the local filesystem."""

    @classmethod
    def from_uri(cls, uri: str) -> "FileFilter":
        if not uri.startswith("file://"):
            raise ValueError("URI must start with file://")
        path = Path(uri[7:]).resolve()
        return cls(output_dir=path)

    def _full_key(self, key: str, *, allow_empty: bool = True) -> Path:
        # Keep the public sha256:<digest> object ID, but use a portable path.
        if key.startswith("sha256:"):
            key = "sha256/" + key[len("sha256:") :]
        return super()._full_key(key, allow_empty=allow_empty)

    def download(self, key: str) -> BinaryIO:
        """Read portable objects, falling back to legacy Unix object names."""
        try:
            return super().download(key)
        except FileNotFoundError:
            if os.name == "nt" or not key.startswith("sha256:"):
                raise
            legacy = super()._full_key(key, allow_empty=False)
            return io.BytesIO(legacy.read_bytes())


__all__ = ["FileFilter"]
