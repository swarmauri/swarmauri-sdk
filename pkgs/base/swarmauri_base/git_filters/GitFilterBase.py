from __future__ import annotations

import hashlib
import io
from abc import abstractmethod
from typing import BinaryIO

from swarmauri_core.git_filters import IGitFilter


class GitFilterBase(IGitFilter):
    """Base class providing ``clean`` and ``smudge`` helpers."""

    @abstractmethod
    def upload(self, key: str, data: BinaryIO) -> str:  # pragma: no cover - interface
        """Store *data* under *key* and return a URI or identifier."""

    @abstractmethod
    def download(self, key: str) -> BinaryIO:  # pragma: no cover - interface
        """Return a binary file-like object for *key*."""

    @classmethod
    @abstractmethod
    def from_uri(cls, uri: str) -> "GitFilterBase":  # pragma: no cover - interface
        """Create a filter instance from *uri*."""

    def clean(self, data: bytes) -> str:
        oid = "sha256:" + hashlib.sha256(data).hexdigest()
        try:
            self.download(oid)
        except FileNotFoundError:
            self.upload(oid, io.BytesIO(data))
        return oid

    def smudge(self, oid: str) -> bytes:
        with self.download(oid) as fh:
            return fh.read()
