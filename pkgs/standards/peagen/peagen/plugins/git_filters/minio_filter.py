"""Storage adapter for MinIO/S3-compatible object stores.

Requires the ``minio`` Python package.
"""

from __future__ import annotations

import io
import os
import shutil
from pathlib import Path
from typing import BinaryIO, Optional

from minio import Minio
from minio.error import S3Error
from pydantic import SecretStr

from peagen._utils.config_loader import load_peagen_toml


class MinioFilter:
    """Simple wrapper around the MinIO client for use with Peagen."""

    def __init__(
        self,
        endpoint: str,
        access_key: SecretStr,
        secret_key: SecretStr,
        bucket: str,
        *,
        secure: bool = True,
        prefix: str = "",
    ) -> None:
        self._client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )
        self._endpoint = endpoint
        self._secure = secure
        self._bucket = bucket
        self._prefix = prefix.lstrip("/")

        if not self._client.bucket_exists(bucket):
            self._client.make_bucket(bucket)

    # ------------------------------------------------------------------
    def _full_key(self, key: str) -> str:
        """Return ``prefix/key`` if a prefix is configured."""
        key = key.lstrip("/")
        if self._prefix:
            return f"{self._prefix.rstrip('/')}/{key}"
        return key

    # ------------------------------------------------------------------
    @property
    def root_uri(self) -> str:
        """Return the base URI as ``minio[s]://endpoint/bucket/prefix/``."""
        scheme = "minios" if self._secure else "minio"
        base = f"{scheme}://{self._endpoint}/{self._bucket}"
        uri = f"{base}/{self._prefix.rstrip('/')}" if self._prefix else base
        return uri.rstrip("/") + "/"

    # ------------------------------------------------------------------
    def upload(self, key: str, data: BinaryIO) -> str:
        """Upload *data* to ``bucket/prefix/key`` and return the artifact URI."""
        size: Optional[int] = None
        try:
            size = os.fstat(data.fileno()).st_size  # type: ignore[attr-defined]
        except Exception:
            if not isinstance(data, (io.BytesIO, io.BufferedReader)):
                data = io.BytesIO(data.read())  # type: ignore[arg-type]
            size = len(data.getbuffer())  # type: ignore[attr-defined]
        data.seek(0)
        self._client.put_object(
            self._bucket,
            self._full_key(key),
            data,
            length=size if size and size > 0 else -1,
            part_size=10 * 1024 * 1024,
        )

        return f"{self.root_uri}{key.lstrip('/')}"

    # ------------------------------------------------------------------
    def download(self, key: str) -> BinaryIO:
        """Return a ``BytesIO`` for the object ``prefix/key``."""
        try:
            resp = self._client.get_object(self._bucket, self._full_key(key))
            buffer = io.BytesIO(resp.read())
            buffer.seek(0)
            resp.close()
            resp.release_conn()
            return buffer
        except S3Error as exc:
            raise FileNotFoundError(f"{self._bucket}/{key}: {exc}") from exc

    # ------------------------------------------------------------------
    def upload_dir(self, src: str | os.PathLike, *, prefix: str = "") -> None:
        """Recursively upload a directory under ``prefix``."""
        base = Path(src)
        for path in base.rglob("*"):
            if path.is_file():
                rel = path.relative_to(base).as_posix()
                key = f"{prefix.rstrip('/')}/{rel}" if prefix else rel
                with path.open("rb") as fh:
                    self.upload(key, fh)

    # ------------------------------------------------------------------
    def iter_prefix(self, prefix: str):
        """Yield keys under ``prefix`` relative to the run root."""
        for obj in self._client.list_objects(
            self._bucket, prefix=prefix, recursive=True
        ):
            key = obj.object_name
            if self._prefix and key.startswith(self._prefix.rstrip("/") + "/"):
                key = key[len(self._prefix.rstrip("/")) + 1 :]
            yield key

    # ------------------------------------------------------------------
    def download_prefix(self, prefix: str, dest_dir: str | os.PathLike) -> None:
        """Download everything under ``prefix`` into ``dest_dir``."""
        dest = Path(dest_dir)
        for rel_key in self.iter_prefix(prefix):
            target = dest / rel_key
            target.parent.mkdir(parents=True, exist_ok=True)
            data = self.download(rel_key)
            with target.open("wb") as fh:
                shutil.copyfileobj(data, fh)

    # ------------------------------------------------------------------
    @classmethod
    def from_uri(cls, uri: str) -> "MinioFilter":
        """Create an adapter from a ``minio[s]://`` URI and env/TOML creds."""
        from urllib.parse import urlparse

        p = urlparse(uri)
        secure = p.scheme == "minios"
        endpoint = p.netloc
        bucket, *rest = p.path.lstrip("/").split("/", 1)
        prefix = rest[0] if rest else ""

        cfg = load_peagen_toml()
        minio_cfg = cfg.get("storage", {}).get("filters", {}).get("minio", {})

        access_key = minio_cfg.get("access_key") or os.getenv("MINIO_ACCESS_KEY", "")
        secret_key = minio_cfg.get("secret_key") or os.getenv("MINIO_SECRET_KEY", "")

        return cls(
            endpoint=endpoint,
            bucket=bucket,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
            prefix=prefix,
        )

    # ---------------------------------------------------------------- oid helpers
    def clean(self, data: bytes) -> str:
        """Store *data* under its SHA256 and return the OID."""
        import hashlib

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
