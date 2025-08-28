from __future__ import annotations

from abc import ABC, abstractmethod
from typing import BinaryIO


class IGitFilter(ABC):
    """Interface for git filters used by Peagen."""

    @classmethod
    @abstractmethod
    def from_uri(cls, uri: str) -> "IGitFilter":
        """Create a filter instance from *uri*."""

    @abstractmethod
    def upload(self, key: str, data: BinaryIO) -> str:
        """Store *data* under *key* and return a URI or identifier."""

    @abstractmethod
    def download(self, key: str) -> BinaryIO:
        """Return a binary file-like object for *key*."""

    @abstractmethod
    def clean(self, data: bytes) -> str:
        """Store *data* and return an object identifier."""

    @abstractmethod
    def smudge(self, oid: str) -> bytes:
        """Retrieve the bytes for *oid*."""
