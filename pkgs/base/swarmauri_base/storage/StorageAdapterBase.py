from __future__ import annotations

import io
import os
import re
from typing import BinaryIO, Optional, Literal
from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.storage.IStorageAdapter import IStorageAdapter


class StorageAdapterBase(IStorageAdapter, ComponentBase):
    """Abstract base class for storage adapters."""

    resource: Optional[str] = Field(
        default=ResourceTypes.STORAGE_ADAPTER.value, frozen=True
    )
    type: Literal["StorageAdapterBase"] = "StorageAdapterBase"

    # ------------------------------------------------------------------
    def upload(self, key: str, data: BinaryIO) -> str:
        raise NotImplementedError("upload() must be implemented by subclass")

    # ------------------------------------------------------------------
    def download(self, key: str) -> BinaryIO:
        raise NotImplementedError("download() must be implemented by subclass")

    # ------------------------------------------------------------------
    def get_blob(self, key: str) -> bytes:
        stream = self.download(key)
        try:
            return stream.read()
        finally:
            close = getattr(stream, "close", None)
            if callable(close):
                close()

    # ------------------------------------------------------------------
    def put_blob(self, key: str, data: bytes) -> str:
        buffer = io.BytesIO(data)
        return self.upload(key, buffer)

    # ------------------------------------------------------------------
    def upload_dir(self, src: str | os.PathLike, *, prefix: str = "") -> None:
        raise NotImplementedError("upload_dir() must be implemented by subclass")

    # ------------------------------------------------------------------
    def push(self, src: str | os.PathLike, *, prefix: str = "") -> None:
        self.upload_dir(src, prefix=prefix)

    # ------------------------------------------------------------------
    def download_dir(self, prefix: str, dest_dir: str | os.PathLike) -> None:
        raise NotImplementedError("download_dir() must be implemented by subclass")

    # ------------------------------------------------------------------
    def pull(self, prefix: str, dest_dir: str | os.PathLike) -> None:
        self.download_dir(prefix, dest_dir)

    # ------------------------------------------------------------------
    async def ensure_bucket(self) -> None:
        return

    # ------------------------------------------------------------------
    async def put_bytes(self, object_key: str, data: bytes, content_type: str) -> None:
        del content_type
        self.put_blob(object_key, data)

    # ------------------------------------------------------------------
    async def get_bytes(self, object_key: str) -> bytes:
        return self.get_blob(object_key)

    # ------------------------------------------------------------------
    def _parse_range(self, start: int, length: int, total: int) -> tuple[int, int]:
        if total < 0:
            raise ValueError("total must be >= 0")
        if start < 0:
            raise ValueError("start must be >= 0")
        if length <= 0:
            raise ValueError("length must be > 0")
        if start >= total:
            raise ValueError("range start out of bounds")

        end_exclusive = min(start + length, total)
        if end_exclusive <= start:
            raise ValueError("invalid range interval")
        return start, end_exclusive

    # ------------------------------------------------------------------
    def _parse_range_header(
        self, range_header: str, total_size: int
    ) -> tuple[int, int]:
        """Return inclusive ``(start, end)`` for a valid HTTP Range header."""
        if total_size <= 0:
            raise ValueError("total_size must be > 0")

        m = re.fullmatch(r"bytes=(\d*)-(\d*)", range_header.strip())
        if not m:
            raise ValueError("invalid range header")

        start_s, end_s = m.group(1), m.group(2)

        if start_s == "" and end_s == "":
            raise ValueError("invalid range header")

        if start_s == "":
            suffix_len = int(end_s)
            if suffix_len <= 0:
                raise ValueError("invalid suffix length")
            start = max(total_size - suffix_len, 0)
            end = total_size - 1
            return start, end

        start = int(start_s)
        if start >= total_size:
            raise ValueError("range start out of bounds")

        if end_s == "":
            end = total_size - 1
        else:
            end = min(int(end_s), total_size - 1)

        if end < start:
            raise ValueError("invalid range interval")

        return start, end

    # ------------------------------------------------------------------
    async def get_range(self, object_key: str, start: int, length: int) -> bytes:
        payload = await self.get_bytes(object_key)
        parsed_start, parsed_end = self._parse_range(start, length, len(payload))
        return payload[parsed_start:parsed_end]

    # ------------------------------------------------------------------
    async def remove_object(self, object_key: str) -> None:
        raise NotImplementedError("remove_object() must be implemented by subclass")

    # ------------------------------------------------------------------
    @classmethod
    def from_uri(cls, uri: str) -> "StorageAdapterBase":
        raise NotImplementedError("from_uri() must be implemented by subclass")
