from __future__ import annotations

import os
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
    def upload_dir(self, src: str | os.PathLike, *, prefix: str = "") -> None:
        raise NotImplementedError("upload_dir() must be implemented by subclass")

    # ------------------------------------------------------------------
    def download_dir(self, prefix: str, dest_dir: str | os.PathLike) -> None:
        raise NotImplementedError("download_dir() must be implemented by subclass")

    # ------------------------------------------------------------------
    @classmethod
    def from_uri(cls, uri: str) -> "StorageAdapterBase":
        raise NotImplementedError("from_uri() must be implemented by subclass")
