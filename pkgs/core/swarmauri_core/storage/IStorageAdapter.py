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
    def get_blob(self, key: str) -> bytes:  # pragma: no cover - interface
        """Retrieve the artifact stored at *key* as raw bytes."""
        raise NotImplementedError

    @abstractmethod
    def put_blob(self, key: str, data: bytes) -> str:  # pragma: no cover - interface
        """Upload raw *data* under *key* and return the resulting URI."""
        raise NotImplementedError

    @abstractmethod
    def upload_dir(
        self, src: str | os.PathLike, *, prefix: str = ""
    ) -> None:  # pragma: no cover - interface
        """Recursively upload files from *src* under *prefix*."""
        raise NotImplementedError

    @abstractmethod
    def push(
        self, src: str | os.PathLike, *, prefix: str = ""
    ) -> None:  # pragma: no cover - interface
        """Convenience wrapper to upload a directory tree."""
        raise NotImplementedError

    @abstractmethod
    def download_dir(
        self, prefix: str, dest_dir: str | os.PathLike
    ) -> None:  # pragma: no cover - interface
        """Download all artifacts under *prefix* into *dest_dir*."""
        raise NotImplementedError

    @abstractmethod
    def pull(
        self, prefix: str, dest_dir: str | os.PathLike
    ) -> None:  # pragma: no cover - interface
        """Convenience wrapper to download a directory tree."""
        raise NotImplementedError

    @abstractmethod
    async def ensure_bucket(self) -> None:  # pragma: no cover - interface
        """Ensure the backing storage container exists."""
        raise NotImplementedError

    @abstractmethod
    async def put_bytes(
        self, object_key: str, data: bytes, content_type: str
    ) -> None:  # pragma: no cover - interface
        """Store raw bytes under *object_key*."""
        raise NotImplementedError

    @abstractmethod
    async def get_bytes(self, object_key: str) -> bytes:  # pragma: no cover - interface
        """Retrieve the stored object as bytes."""
        raise NotImplementedError

    @abstractmethod
    async def get_range(
        self, object_key: str, start: int, length: int
    ) -> bytes:  # pragma: no cover - interface
        """Retrieve a byte range from a stored object."""
        raise NotImplementedError

    @abstractmethod
    def _parse_range(self, start: int, length: int, total: int) -> tuple[int, int]:
        """Normalize and validate byte range values."""
        raise NotImplementedError

    @abstractmethod
    def _parse_range_header(
        self, range_header: str, total_size: int
    ) -> tuple[int, int]:
        """Parse an HTTP Range header and return inclusive ``(start, end)``."""
        raise NotImplementedError

    @abstractmethod
    async def remove_object(
        self, object_key: str
    ) -> None:  # pragma: no cover - interface
        """Delete an object from storage if it exists."""
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def from_uri(cls, uri: str) -> "IStorageAdapter":  # pragma: no cover - interface
        """Create an adapter instance from *uri*."""
        raise NotImplementedError
