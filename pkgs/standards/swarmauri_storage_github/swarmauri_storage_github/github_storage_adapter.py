from __future__ import annotations

import os
from typing import BinaryIO

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.storage import StorageAdapterBase


@ComponentBase.register_type(StorageAdapterBase, "GithubStorageAdapter")
class GithubStorageAdapter(StorageAdapterBase):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.kwargs = kwargs

    def upload(self, key: str, data: BinaryIO) -> str:  # pragma: no cover - stub
        return f"github://{key}"

    def download(self, key: str) -> BinaryIO:  # pragma: no cover - stub
        raise NotImplementedError("download() not implemented")

    def upload_dir(
        self, src: str | os.PathLike, *, prefix: str = ""
    ) -> None:  # pragma: no cover - stub
        raise NotImplementedError("upload_dir() not implemented")

    def download_dir(
        self, prefix: str, dest_dir: str | os.PathLike
    ) -> None:  # pragma: no cover - stub
        raise NotImplementedError("download_dir() not implemented")

    @classmethod
    def from_uri(cls, uri: str) -> "GithubStorageAdapter":  # pragma: no cover - stub
        return cls()
