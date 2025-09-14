"""Storage adapter and Git filter backed by a MinIO or S3-compatible service."""

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
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.storage import StorageAdapterBase
from swarmauri_base.git_filters import GitFilterBase


@ComponentBase.register_type(StorageAdapterBase, "MinioFilter")
class MinioFilter(StorageAdapterBase, GitFilterBase):
    """Interact with MinIO for storing Git objects.

    Provides helpers to upload and download individual files or directory
    trees, allowing Peagen to offload repository data to object storage.
    """

    def __init__(
        self,
        endpoint: str,
        access_key: SecretStr,
        secret_key: SecretStr,
        bucket: str,
        *,
        secure: bool = True,
        prefix: str = "",
        **kwargs,
    ) -> None:
        """Create a new MinioFilter instance.

        endpoint (str): Host and port of the MinIO service.
        access_key (SecretStr): Access key credential.
        secret_key (SecretStr): Secret key credential.
        bucket (str): Bucket name to store objects in.
        secure (bool): Use HTTPS when ``True``.
        prefix (str): Optional path prefix inside the bucket.
        **kwargs: Additional options forwarded to ``StorageAdapterBase``.

        RETURNS (None): This method does not return anything.
        """
        super().__init__(**kwargs)
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

    def _full_key(self, key: str) -> str:
        key = key.lstrip("/")
        if self._prefix:
            return f"{self._prefix.rstrip('/')}/{key}"
        return key

    @property
    def root_uri(self) -> str:
        """Return the root URI for the configured bucket and prefix.

        RETURNS (str): Base MinIO URI ending with a trailing slash.
        """
        scheme = "minios" if self._secure else "minio"
        base = f"{scheme}://{self._endpoint}/{self._bucket}"
        uri = f"{base}/{self._prefix.rstrip('/')}" if self._prefix else base
        return uri.rstrip("/") + "/"

    def upload(self, key: str, data: BinaryIO) -> str:
        """Upload a binary stream to the bucket.

        key (str): Destination object key.
        data (BinaryIO): File-like object containing the data.

        RETURNS (str): URI of the stored object.
        RAISES (S3Error): If the upload fails.
        """
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

    def download(self, key: str) -> BinaryIO:
        """Retrieve an object from the bucket.

        key (str): Object key to fetch.

        RETURNS (BinaryIO): Buffer containing the object data.
        RAISES (FileNotFoundError): If the object cannot be found.
        """
        try:
            resp = self._client.get_object(self._bucket, self._full_key(key))
            buffer = io.BytesIO(resp.read())
            buffer.seek(0)
            resp.close()
            resp.release_conn()
            return buffer
        except S3Error as exc:
            raise FileNotFoundError(f"{self._bucket}/{key}: {exc}") from exc

    def upload_dir(self, src: str | os.PathLike, *, prefix: str = "") -> None:
        """Upload all files under a directory to the bucket.

        src (str | os.PathLike): Local directory to walk.
        prefix (str): Optional key prefix to prepend to uploaded objects.

        RETURNS (None): This method does not return anything.
        """
        base = Path(src)
        for path in base.rglob("*"):
            if path.is_file():
                rel = path.relative_to(base).as_posix()
                key = f"{prefix.rstrip('/')}/{rel}" if prefix else rel
                with path.open("rb") as fh:
                    self.upload(key, fh)

    def iter_prefix(self, prefix: str):
        """Iterate over object keys matching a prefix.

        prefix (str): Key prefix to match.

        RETURNS (Iterator[str]): Relative keys under the configured prefix.
        """
        for obj in self._client.list_objects(
            self._bucket, prefix=prefix, recursive=True
        ):
            key = obj.object_name
            if self._prefix and key.startswith(self._prefix.rstrip("/") + "/"):
                key = key[len(self._prefix.rstrip("/")) + 1 :]
            yield key

    def download_prefix(self, prefix: str, dest_dir: str | os.PathLike) -> None:
        """Download all objects beneath a prefix into a directory.

        prefix (str): Key prefix to copy from the bucket.
        dest_dir (str | os.PathLike): Local directory to populate.

        RETURNS (None): This method does not return anything.
        """
        dest = Path(dest_dir)
        for rel_key in self.iter_prefix(prefix):
            target = dest / rel_key
            target.parent.mkdir(parents=True, exist_ok=True)
            data = self.download(rel_key)
            with target.open("wb") as fh:
                shutil.copyfileobj(data, fh)

    @classmethod
    def from_uri(cls, uri: str) -> "MinioFilter":
        """Create a MinioFilter from a connection string.

        uri (str): A URI like ``minio://host:port/bucket/prefix``.

        RETURNS (MinioFilter): Configured ``MinioFilter`` instance.
        """
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


__all__ = ["MinioFilter"]
