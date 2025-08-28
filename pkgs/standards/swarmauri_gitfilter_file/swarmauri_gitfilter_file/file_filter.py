from __future__ import annotations

from pathlib import Path

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


__all__ = ["FileFilter"]
