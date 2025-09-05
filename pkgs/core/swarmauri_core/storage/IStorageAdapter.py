from __future__ import annotations

from abc import ABC, abstractmethod
import os
from typing import BinaryIO


class IStorageAdapter(ABC):
    """Interface for basic storage adapter operations."""

    @abstractmethod
    def upload(self, key: str, data: BinaryIO) -> str:  # pragma: no cover - interface
        """Upload *data* under *key* and return the resulting URI."""
        raise NotImplementedError

    @abstractmethod
    def download(self, key: str) -> BinaryIO:  # pragma: no cover - interface
        """Retrieve the artifact stored at *key*."""
        raise NotImplementedError

    @abstractmethod
    def upload_dir(
        self, src: str | os.PathLike, *, prefix: str = ""
    ) -> None:  # pragma: no cover - interface
        """Recursively upload files from *src* under *prefix*."""
        raise NotImplementedError

    @abstractmethod
    def download_dir(
        self, prefix: str, dest_dir: str | os.PathLike
    ) -> None:  # pragma: no cover - interface
        """Download all artifacts under *prefix* into *dest_dir*."""
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def from_uri(cls, uri: str) -> "IStorageAdapter":  # pragma: no cover - interface
        """Create an adapter instance from *uri*."""
        raise NotImplementedError
