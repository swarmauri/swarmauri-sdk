from __future__ import annotations

from typing import BinaryIO
import s3fs


class S3FSFilter:
    """Simple S3 storage using :mod:`s3fs` for Git filters."""

    def __init__(self, bucket: str, **kwargs) -> None:
        self.bucket = bucket.rstrip("/")
        self.fs = s3fs.S3FileSystem(**kwargs)

    def _full_key(self, key: str) -> str:
        return f"{self.bucket}/{key.lstrip('/')}"

    def upload(self, key: str, data: BinaryIO) -> str:
        dest = self._full_key(key)
        with self.fs.open(dest, "wb") as fh:
            fh.write(data.read())
        return f"s3://{dest}"

    def download(self, key: str) -> BinaryIO:
        src = self._full_key(key)
        return self.fs.open(src, "rb")

    @classmethod
    def from_uri(cls, uri: str) -> "S3FSFilter":
        scheme, _, path = uri.partition("://")
        if scheme != "s3":
            raise ValueError("URI must be s3://bucket")
        bucket = path.strip("/")
        return cls(bucket=bucket)

    # ---------------------------------------------------------------- oid helpers
    def clean(self, data: bytes) -> str:
        import hashlib
        import io
        oid = "sha256:" + hashlib.sha256(data).hexdigest()
        try:
            self.download(oid)
        except FileNotFoundError:
            self.upload(oid, io.BytesIO(data))
        return oid

    def smudge(self, oid: str) -> bytes:
        with self.download(oid) as fh:
            return fh.read()
