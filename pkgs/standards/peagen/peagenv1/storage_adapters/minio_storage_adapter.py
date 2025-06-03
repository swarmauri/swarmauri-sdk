"""
Storage adapter for MinIO / S3-compatible object stores.

Depends on the ``minio`` Python package.
"""

from __future__ import annotations

import io
import os
import posixpath
import shutil
from pathlib import Path
from typing import BinaryIO, Optional

from minio import Minio
from minio.error import S3Error
from pydantic import SecretStr

from peagen.cli_common import load_peagen_toml


# ────────────────────────────────────────────────────────────────────────────
# helpers
# ────────────────────────────────────────────────────────────────────────────
def _to_posix(path: str) -> str:
    """Convert OS path to clean POSIX key (no leading “/”)."""
    return posixpath.normpath(path.lstrip("/").replace("\\", "/"))


# ────────────────────────────────────────────────────────────────────────────
# adapter
# ────────────────────────────────────────────────────────────────────────────
class MinioStorageAdapter:
    """
    Small wrapper around the MinIO client that fulfils Peagen’s
    IStorageAdapter contract.

    * All public methods accept *any* path style.
    * Keys are normalised to POSIX before hitting the MinIO client.
    """

    # ───────────────────────────────────────────────────────── constructor ──
    def __init__(
        self,
        endpoint: str,
        access_key: SecretStr | str,
        secret_key: SecretStr | str,
        bucket: str,
        *,
        secure: bool = True,
        prefix: str = "",
        part_size: int = 10 * 1024 * 1024,
    ):
        self._client = Minio(
            endpoint,
            access_key=str(access_key),
            secret_key=str(secret_key),
            secure=secure,
        )
        self._bucket = bucket
        self._secure = secure
        self._endpoint = endpoint
        self._prefix = _to_posix(prefix) if prefix else ""
        self._part_size = part_size

        # auto-create bucket if missing
        if not self._client.bucket_exists(bucket):
            self._client.make_bucket(bucket)

    # ──────────────────────────────────────────── internal helpers ──
    def _full_key(self, key: str) -> str:
        """Return `<prefix>/<key>` (both POSIX), collapsed & deduped."""
        key_posix = _to_posix(key)
        if self._prefix:
            return _to_posix(f"{self._prefix}/{key_posix}")
        return key_posix

    # ─────────────────────────────────────────── public properties ──
    @property
    def root_uri(self) -> str:
        """A canonical URI for this adapter: ``minio[s]://endpoint/bucket/prefix/``."""
        scheme = "minios" if self._secure else "minio"
        base = f"{scheme}://{self._endpoint}/{self._bucket}"
        uri = f"{base}/{self._prefix}" if self._prefix else base
        return uri.rstrip("/") + "/"

    # ───────────────────────────────────────────────────────── upload ──
    def upload(self, key: str, data: BinaryIO) -> None:
        """Upload *data* to ``<bucket>/<prefix>/<key>``."""
        size: Optional[int]
        try:
            size = os.fstat(data.fileno()).st_size  # type: ignore[attr-defined]
        except Exception:
            # Fallback for BytesIO / wrapped streams
            if not isinstance(data, (io.BytesIO, io.BufferedReader)):
                data = io.BytesIO(data.read())  # type: ignore[arg-type]
            size = len(data.getbuffer())  # type: ignore[attr-defined]
        data.seek(0)

        self._client.put_object(
            bucket_name=self._bucket,
            object_name=self._full_key(key),
            data=data,
            length=size if size > 0 else -1,
            part_size=self._part_size,
        )

    # ─────────────────────────────────────────────────────── download ──
    def download(self, key: str) -> BinaryIO:
        """Return a BytesIO of the object ``<prefix>/<key>``."""
        try:
            resp = self._client.get_object(self._bucket, self._full_key(key))
            buf = io.BytesIO(resp.read())
            buf.seek(0)
            resp.close()
            resp.release_conn()
            return buf
        except S3Error as exc:  # pragma: no cover
            raise FileNotFoundError(f"{self._bucket}/{key}: {exc}") from exc

    # ─────────────────────────────────────────────────── upload_dir ──
    def upload_dir(self, src: str | os.PathLike, *, prefix: str = "") -> None:
        """Recursively upload directory *src* below ``prefix``."""
        base = Path(src)
        for path in base.rglob("*"):
            if path.is_file():
                rel = path.relative_to(base).as_posix()
                key = f"{prefix.rstrip('/')}/{rel}" if prefix else rel
                with path.open("rb") as fh:
                    self.upload(key, fh)

    # ─────────────────────────────────────────────────── iter_prefix ──
    def iter_prefix(self, prefix: str):
        """Yield keys (relative to run root) under **prefix**."""
        target = self._full_key(prefix)
        for obj in self._client.list_objects(self._bucket, prefix=target, recursive=True):
            key = obj.object_name
            # drop global prefix (if any) so callers see relative keys
            if self._prefix and key.startswith(self._prefix + "/"):
                key = key[len(self._prefix) + 1 :]
            yield key

    # ───────────────────────────────────────────────── download_prefix ──
    def download_prefix(self, prefix: str, dest_dir: str | os.PathLike) -> None:
        """Download *all* objects under **prefix** into *dest_dir*."""
        dest = Path(dest_dir)
        for rel_key in self.iter_prefix(prefix):
            target = dest / rel_key
            target.parent.mkdir(parents=True, exist_ok=True)
            data = self.download(rel_key)
            with target.open("wb") as fh:
                shutil.copyfileobj(data, fh)

    # ───────────────────────────────────────────────────────── exists ──
    def exists(self, key: str) -> bool:
        """Return ``True`` if the object exists in the bucket."""
        try:
            self._client.stat_object(self._bucket, self._full_key(key))
            return True
        except S3Error:
            return False

    # ──────────────────────────────────────────────── from_uri helper ──
    @classmethod
    def from_uri(cls, uri: str) -> "MinioStorageAdapter":
        """
        Build adapter from a ``minio[s]://`` URI, env-vars or TOML for creds.

        Example URI: ``minios://localhost:9000/mybucket/some/prefix``.
        """
        from urllib.parse import urlparse

        p = urlparse(uri)
        secure = p.scheme == "minios"
        endpoint = p.netloc
        bucket, *rest = _to_posix(p.path).split("/", 1)
        prefix = rest[0] if rest else ""

        # credentials from env or ~/.config/peagen.toml
        cfg = load_peagen_toml()
        minio_cfg = cfg.get("storage", {}).get("adapters", {}).get("minio", {})

        access_key = minio_cfg.get("access_key") or os.getenv("MINIO_ACCESS_KEY", "")
        secret_key = minio_cfg.get("secret_key") or os.getenv("MINIO_SECRET_KEY", "")

        return cls(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            bucket=bucket,
            secure=secure,
            prefix=prefix,
        )
