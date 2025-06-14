"""S3-compatible storage adapter implemented with s3fs."""

from __future__ import annotations

import io
import os
import shutil
from pathlib import Path
from typing import BinaryIO

import s3fs


class S3FSStorageAdapter:
    """Store and retrieve artifacts using an S3 bucket via s3fs."""

    def __init__(self, bucket: str, *, prefix: str = "", **fs_kwargs) -> None:
        self._bucket = bucket
        self._prefix = prefix.lstrip("/")
        self._fs = s3fs.S3FileSystem(**fs_kwargs)

    # ------------------------------------------------------------------
    def _full_key(self, key: str) -> str:
        key = key.lstrip("/")
        if self._prefix:
            return f"{self._prefix.rstrip('/')}/{key}"
        return key

    @property
    def root_uri(self) -> str:
        """Return the base ``s3://`` URI for this adapter."""
        base = f"s3://{self._bucket}"
        uri = f"{base}/{self._prefix.rstrip('/')}" if self._prefix else base
        return uri.rstrip("/") + "/"

    # ------------------------------------------------------------------
    def upload(self, key: str, data: BinaryIO) -> str:
        """Upload ``data`` to ``bucket/prefix/key`` and return the artifact URI."""
        dest = f"{self._bucket}/{self._full_key(key)}"
        data.seek(0)
        with self._fs.open(dest, "wb") as fh:
            shutil.copyfileobj(data, fh)
        return f"{self.root_uri}{key.lstrip('/')}"

    # ------------------------------------------------------------------
    def download(self, key: str) -> BinaryIO:
        """Return the contents of ``bucket/prefix/key`` as a ``BytesIO``."""
        path = f"{self._bucket}/{self._full_key(key)}"
        if not self._fs.exists(path):
            raise FileNotFoundError(path)
        with self._fs.open(path, "rb") as fh:
            buffer = io.BytesIO(fh.read())
        buffer.seek(0)
        return buffer

    # ------------------------------------------------------------------
    def upload_dir(self, src: str | os.PathLike, *, prefix: str = "") -> None:
        """Recursively upload all files under ``src`` using an optional prefix."""
        base = Path(src)
        for path in base.rglob("*"):
            if path.is_file():
                rel = path.relative_to(base).as_posix()
                key = f"{prefix.rstrip('/')}/{rel}" if prefix else rel
                with path.open("rb") as fh:
                    self.upload(key, fh)

    # ------------------------------------------------------------------
    def iter_prefix(self, prefix: str):
        """Yield stored keys beginning with ``prefix``."""
        base = self._full_key(prefix).rstrip("/")
        prefix_path = f"{self._bucket}/{base}" if base else self._bucket
        for path in self._fs.find(prefix_path):
            key = path[len(f"{self._bucket}/") :]
            if self._prefix and key.startswith(self._prefix.rstrip("/") + "/"):
                key = key[len(self._prefix.rstrip("/")) + 1 :]
            yield key

    # ------------------------------------------------------------------
    def download_prefix(self, prefix: str, dest_dir: str | os.PathLike) -> None:
        """Download all objects under ``prefix`` into ``dest_dir``."""
        dest = Path(dest_dir)
        for rel_key in self.iter_prefix(prefix):
            target = dest / rel_key
            target.parent.mkdir(parents=True, exist_ok=True)
            data = self.download(rel_key)
            with target.open("wb") as fh:
                shutil.copyfileobj(data, fh)

    # ------------------------------------------------------------------
    @classmethod
    def from_uri(cls, uri: str, **fs_kwargs) -> "S3FSStorageAdapter":
        """Instantiate the adapter from an ``s3://`` URI."""
        from urllib.parse import urlparse

        p = urlparse(uri)
        bucket, *rest = p.path.lstrip("/").split("/", 1)
        prefix = rest[0] if rest else ""
        return cls(bucket=bucket or p.netloc, prefix=prefix, **fs_kwargs)


__all__ = ["S3FSStorageAdapter"]

