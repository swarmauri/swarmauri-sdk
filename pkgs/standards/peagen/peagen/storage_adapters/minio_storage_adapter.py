"""Storage adapter for MinIO/S3-compatible object stores.

Requires the ``minio`` Python package.
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

from peagen.cli_common import load_peagen_toml


class MinioStorageAdapter:
    """
    Very small wrapper around the MinIO client that fulfils Peagen’s
    IStorageAdapter contract, now prefix-aware.
    """

    # ──────────────────────────────────────────────────────────────── ctor ──
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

        # auto-create bucket if necessary
        if not self._client.bucket_exists(bucket):
            self._client.make_bucket(bucket)

    # ──────────────────────────────────────────── internal helpers ──
    def _full_key(self, key: str) -> str:
        """
        Return `self._prefix/key` if a prefix is configured, else `key`.
        Ensures exactly one “/” between parts.
        """
        key = key.lstrip("/")
        if self._prefix:
            return f"{self._prefix.rstrip('/')}/{key}"
        return key

    # ─────────────────────────────────────────── public properties ──
    @property
    def root_uri(self) -> str:  # MINIO scheme with trailing “/”
        scheme = "minios" if self._secure else "minio"
        base = f"{scheme}://{self._endpoint}/{self._bucket}"
        uri = f"{base}/{self._prefix.rstrip('/')}" if self._prefix else base
        return uri.rstrip("/") + "/"

    # ───────────────────────────────────────────────────────── upload ──
    def upload(self, key: str, data: BinaryIO) -> None:
        """
        Store *data* at `<bucket>/<prefix>/<key>` (prefix honoured).
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
            length=size if size > 0 else -1,
            part_size=10 * 1024 * 1024,
        )

    # ─────────────────────────────────────────────────────── download ──
    def download(self, key: str) -> BinaryIO:
        """
        Retrieve object `<prefix>/<key>` and return a BytesIO.
        """
        try:
            print(f"downloading {key}")
            resp = self._client.get_object(self._bucket, self._full_key(key))
            buffer = io.BytesIO(resp.read())
            buffer.seek(0)
            resp.close()
            resp.release_conn()
            return buffer
        except S3Error as exc:
            raise FileNotFoundError(f"{self._bucket}/{key}: {exc}") from exc

    # ─────────────────────────────────────────────────── upload_dir ──
    def upload_dir(self, src: str | os.PathLike, *, prefix: str = "") -> None:
        """
        Recursively upload directory *src* under `<prefix>/…` (relative
        to the *run* root).
        """
        base = Path(src)
        for path in base.rglob("*"):
            if path.is_file():
                rel = path.relative_to(base).as_posix()
                key = f"{prefix.rstrip('/')}/{rel}" if prefix else rel
                with path.open("rb") as fh:
                    self.upload(key, fh)

    # ─────────────────────────────────────────────────── iter_prefix ──
    def iter_prefix(self, prefix: str):
        """
        Yield keys *relative to the run root* under ``prefix``.
        """
        for obj in self._client.list_objects(
            self._bucket, prefix=prefix, recursive=True
        ):
            key = obj.object_name
            # strip run-prefix before yielding
            if self._prefix and key.startswith(self._prefix.rstrip("/") + "/"):
                key = key[len(self._prefix.rstrip("/")) + 1 :]
            yield key

    # ───────────────────────────────────────────────── download_prefix ──
    def download_prefix(self, prefix: str, dest_dir: str | os.PathLike) -> None:
        """
        Download *all* objects under ``prefix`` (relative to run root)
        into *dest_dir*.
        """
        print(prefix, dest_dir)
        dest = Path(dest_dir)
        for rel_key in self.iter_prefix(prefix):
            target = dest / rel_key
            target.parent.mkdir(parents=True, exist_ok=True)
            print(rel_key)
            data = self.download(rel_key)
            with target.open("wb") as fh:
                shutil.copyfileobj(data, fh)

    # ──────────────────────────────────────────────── from_uri helper ──
    @classmethod
    def from_uri(cls, uri: str) -> "MinioStorageAdapter":
        """
        Build adapter from a ``minio[s]://…`` URI, env vars or TOML for creds.
        """
        from urllib.parse import urlparse

        p = urlparse(uri)
        secure = p.scheme == "minios"
        endpoint = p.netloc
        bucket, *rest = p.path.lstrip("/").split("/", 1)
        prefix = rest[0] if rest else ""

        # env / TOML creds --------------------------------------------------
        cfg = load_peagen_toml()  # ← centralised search
        minio_cfg = cfg.get("storage", {}).get("adapters", {}).get("minio", {})

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
