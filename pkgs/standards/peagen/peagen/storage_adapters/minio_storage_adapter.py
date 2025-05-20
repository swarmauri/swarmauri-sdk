"""
peagen/storage_adapters/minio_storage_adapter.py
─────────────────────────────────────────────────
Concrete implementation of the IStorageAdapter port using the
MinIO Python SDK (S3-compatible object storage).

Install dependency:
    pip install minio
"""

from __future__ import annotations
from pydantic import SecretStr

import io
import os
import shutil
from pathlib import Path
from typing import BinaryIO, Optional

from minio import Minio
from minio.error import S3Error

# from swarmauri_core.storage_adapters.IStorageAdapter import IStorageAdapter


# class MinioStorageAdapter(IStorageAdapter):
class MinioStorageAdapter:
    """
    Very small wrapper around the MinIO client that fulfils the
    two-method IStorageAdapter contract: `upload()` and `download()`.
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
    ):
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

        # create bucket if it doesn't exist
        if not self._client.bucket_exists(bucket):
            self._client.make_bucket(bucket)

    # ------------------------------------------------------------
    #  NEW – where Peagen should tell evaluators to look
    # ------------------------------------------------------------
    @property
    def root_uri(self) -> str:
        scheme = "minios" if self._secure else "minio"
        base   = f"{scheme}://{self._endpoint}/{self._bucket}"
        return f"{base}/{self._prefix}" if self._prefix else base


    # ---------------------------------------------------------------- upload
    def upload(self, key: str, data: BinaryIO) -> None:  # noqa: D401
        """
        Store *data* at `bucket/key`.

        * If the file-like object has a known size (`fileno()`), stream without
          loading into memory.
        * Otherwise read into memory to obtain a length.
        """
        size: Optional[int] = None
        try:
            fileno = data.fileno()  # type: ignore[attr-defined]
            size = os.fstat(fileno).st_size
        except Exception:
            # fallback: read into bytes buffer
            if not isinstance(data, (io.BytesIO, io.BufferedReader)):
                data = io.BytesIO(data.read())  # type: ignore[arg-type]
            size = len(data.getbuffer())  # type: ignore[attr-defined]

        # make sure we start at position 0
        data.seek(0)

        # use unknown-size streaming if size == -1
        self._client.put_object(
            self._bucket,
            key,
            data,
            length=size if size > 0 else -1,
            part_size=10 * 1024 * 1024,
        )

    # ---------------------------------------------------------------- download
    def download(self, key: str) -> BinaryIO:  # noqa: D401
        """
        Retrieve object at `bucket/key` and return it as an in-memory BytesIO.
        """
        try:
            response = self._client.get_object(self._bucket, key)
            # read all parts into memory; caller owns the returned BytesIO
            buffer = io.BytesIO(response.read())
            buffer.seek(0)
            response.close()
            response.release_conn()
            return buffer
        except S3Error as exc:
            raise FileNotFoundError(f"{self._bucket}/{key}: {exc}") from exc

    # ---------------------------------------------------------------- upload_dir
    def upload_dir(self, src: str | os.PathLike, *, prefix: str = "") -> None:
        """Upload the contents of a directory recursively under ``prefix``."""
        base = Path(src)
        for path in base.rglob("*"):
            if path.is_file():
                rel = path.relative_to(base)
                key = os.path.join(self._prefix, key) if self._prefix else key
                with path.open("rb") as fh:
                    self.upload(key, fh)

    # ---------------------------------------------------------------- iter_prefix
    def iter_prefix(self, prefix: str):
        """Iterate over stored keys under ``prefix``."""
        objects = self._client.list_objects(self._bucket, prefix=prefix, recursive=True)
        for obj in objects:
            yield obj.object_name

    # ---------------------------------------------------------------- download_prefix
    def download_prefix(self, prefix: str, dest_dir: str | os.PathLike) -> None:
        """Download objects under ``prefix`` into ``dest_dir``."""
        dest = Path(dest_dir)
        for key in self.iter_prefix(prefix):
            rel = Path(key).relative_to(prefix)
            target = dest / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            data = self.download(key)
            with open(target, "wb") as fh:
                shutil.copyfileobj(data, fh)

    @classmethod
    def from_uri(cls, uri: str) -> "MinioStorageAdapter":
        """
        Build an adapter from a minio[s]:// URI.
        Credentials are read from env vars or from
        [tool.peagen.storage.adapters.minio] in pyproject.toml / .peagen.toml.
        """
        from urllib.parse import urlparse
        import tomllib, os, pathlib

        p = urlparse(uri)
        secure   = p.scheme == "minios"
        endpoint = p.netloc
        bucket, *rest = p.path.lstrip("/").split("/", 1)
        prefix = rest[0] if rest else ""

        # ---- optional config file lookup ---------------------------------
        creds = {"access_key": None, "secret_key": None}
        cfg_file = pathlib.Path(".peagen.toml")
        if cfg_file.exists():
            cfg = tomllib.loads(cfg_file.read_text())
            creds.update(cfg.get("storage", {})
                            .get("adapters", {})
                            .get("minio", {}))

        access = creds["access_key"] or os.getenv("MINIO_ACCESS_KEY") or ""
        secret = creds["secret_key"] or os.getenv("MINIO_SECRET_KEY") or ""

        return cls(
            endpoint=endpoint,
            bucket=bucket,
            access_key=access,
            secret_key=secret,
            secure=secure,
            prefix=prefix,
        )