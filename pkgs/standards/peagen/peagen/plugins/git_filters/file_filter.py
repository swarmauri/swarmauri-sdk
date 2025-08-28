from __future__ import annotations

import io
import hashlib
from pathlib import Path

from swarmauri_storage_file import FileStorageAdapter


class FileFilter(FileStorageAdapter):
    """Git filter that stores files on the local filesystem."""

    @classmethod
    def from_uri(cls, uri: str) -> "FileFilter":
        if not uri.startswith("file://"):
            raise ValueError("URI must start with file://")
        path = Path(uri[7:]).resolve()
        return cls(output_dir=path)

    def clean(self, data: bytes) -> str:
        """Store *data* under its SHA256 and return the OID."""
        oid = "sha256:" + hashlib.sha256(data).hexdigest()
        try:
            self.download(oid)
        except FileNotFoundError:
            self.upload(oid, io.BytesIO(data))
        return oid

    def smudge(self, oid: str) -> bytes:
        """Retrieve the bytes for *oid*."""
        with self.download(oid) as fh:
            return fh.read()
