"""Base class for git filters implementing common clean/smudge helpers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import BinaryIO

from swarmauri_core.git import IGitFilter


class GitFilterBase(IGitFilter, ABC):
    """Abstract base implementing object-id helpers for git filters."""

    @classmethod
    @abstractmethod
    def from_uri(cls, uri: str) -> "GitFilterBase":  # pragma: no cover - interface
        """Create a filter from a URI."""
        ...

    @abstractmethod
    def upload(self, key: str, data: BinaryIO) -> str:  # pragma: no cover - interface
        """Upload *data* under *key* and return an artifact URI."""
        ...

    @abstractmethod
    def download(self, key: str) -> BinaryIO:  # pragma: no cover - interface
        """Return a binary stream for *key*."""
        ...

    def clean(self, data: bytes) -> str:
        """Store *data* under its SHA256 digest and return the object id."""
        import hashlib
        import io

        oid = "sha256:" + hashlib.sha256(data).hexdigest()
        try:
            self.download(oid)
        except FileNotFoundError:
            self.upload(oid, io.BytesIO(data))
        return oid

    def smudge(self, oid: str) -> bytes:
        """Retrieve bytes for *oid*."""
        with self.download(oid) as fh:
            return fh.read()
