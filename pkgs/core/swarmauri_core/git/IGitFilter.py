"""Protocol for git filters used by Peagen."""

from __future__ import annotations

from typing import BinaryIO, Protocol, runtime_checkable


@runtime_checkable
class IGitFilter(Protocol):
    """Interface for filters storing and retrieving blobs by object id."""

    @classmethod
    def from_uri(cls, uri: str) -> "IGitFilter":
        """Create a filter from a URI."""
        ...

    def upload(self, key: str, data: BinaryIO) -> str:
        """Store data under key and return an artifact URI."""
        ...

    def download(self, key: str) -> BinaryIO:
        """Retrieve bytes previously stored under key."""
        ...

    def clean(self, data: bytes) -> str:
        """Store *data* and return the resulting object id."""
        ...

    def smudge(self, oid: str) -> bytes:
        """Return the bytes associated with object id *oid*."""
        ...
