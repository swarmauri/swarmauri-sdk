from __future__ import annotations

import io
import os
import shutil
from pathlib import Path
from typing import BinaryIO

import s3fs
from pydantic import SecretStr

from peagen._utils.config_loader import load_peagen_toml


class S3FSFilter:
    """Git filter that stores artifacts in S3 via :mod:`s3fs`."""

    def __init__(
        self,
        bucket: str,
        *,
        key: SecretStr | str = "",
        secret: SecretStr | str = "",
        endpoint_url: str | None = None,
        region_name: str | None = None,
        prefix: str = "",
        **kwargs,
    ) -> None:
        self._bucket = bucket
        self._prefix = prefix.lstrip("/")

        k = key.get_secret_value() if isinstance(key, SecretStr) else key
        s = secret.get_secret_value() if isinstance(secret, SecretStr) else secret
        client_kwargs: dict[str, str] = {}
        if endpoint_url:
            client_kwargs["endpoint_url"] = endpoint_url
        if region_name:
            client_kwargs["region_name"] = region_name

        self._fs = s3fs.S3FileSystem(
            key=k or None,
            secret=s or None,
            client_kwargs=client_kwargs or None,
            **kwargs,
        )

    # ------------------------------------------------------------------ helpers
    def _full_key(self, key: str) -> str:
        key = key.lstrip("/")
        if self._prefix:
            key = f"{self._prefix.rstrip('/')}/{key}"
        return f"{self._bucket}/{key}"

    @property
    def root_uri(self) -> str:
        """Return the base ``s3://`` URI for this filter."""
        base = f"s3://{self._bucket}"
        uri = f"{base}/{self._prefix.rstrip('/')}" if self._prefix else base
        return uri.rstrip("/") + "/"

    # ------------------------------------------------------------------ uploading
    def upload(self, key: str, data: BinaryIO) -> str:
        dest = self._full_key(key)
        with self._fs.open(dest, "wb") as fh:
            shutil.copyfileobj(data, fh)
        return f"{self.root_uri}{key.lstrip('/')}"

    def download(self, key: str) -> BinaryIO:
        src = self._full_key(key)
        return self._fs.open(src, "rb")

    def upload_dir(self, src: str | os.PathLike, *, prefix: str = "") -> None:
        base = Path(src)
        for path in base.rglob("*"):
            if path.is_file():
                rel = path.relative_to(base).as_posix()
                key = f"{prefix.rstrip('/')}/{rel}" if prefix else rel
                with path.open("rb") as fh:
                    self.upload(key, fh)

    def iter_prefix(self, prefix: str):
        base = self._full_key(prefix)
        for p in self._fs.find(base):
            rel = p[len(f"{self._bucket}/") :]
            if self._prefix and rel.startswith(self._prefix.rstrip("/") + "/"):
                rel = rel[len(self._prefix.rstrip("/")) + 1 :]
            yield rel

    def download_prefix(self, prefix: str, dest_dir: str | os.PathLike) -> None:
        dest = Path(dest_dir)
        for rel_key in self.iter_prefix(prefix):
            target = dest / rel_key
            target.parent.mkdir(parents=True, exist_ok=True)
            data = self.download(rel_key)
            with target.open("wb") as fh:
                shutil.copyfileobj(data, fh)

    @classmethod
    def from_uri(cls, uri: str) -> "S3FSFilter":
        from urllib.parse import urlparse

        p = urlparse(uri)
        if p.scheme != "s3":
            raise ValueError("URI must start with s3://")

        bucket = p.netloc
        prefix = p.path.lstrip("/")

        cfg = load_peagen_toml()
        s3_cfg = cfg.get("storage", {}).get("filters", {}).get("s3fs", {})

        key = s3_cfg.get("key") or os.getenv("AWS_ACCESS_KEY_ID", "")
        secret = s3_cfg.get("secret") or os.getenv("AWS_SECRET_ACCESS_KEY", "")
        endpoint_url = s3_cfg.get("endpoint_url") or os.getenv("AWS_ENDPOINT_URL")
        region = s3_cfg.get("region") or os.getenv("AWS_REGION")

        return cls(
            bucket=bucket,
            prefix=prefix,
            key=key,
            secret=secret,
            endpoint_url=endpoint_url,
            region_name=region,
        )

    # ---------------------------------------------------------------- oid helpers
    def clean(self, data: bytes) -> str:
        import hashlib

        oid = "sha256:" + hashlib.sha256(data).hexdigest()
        try:
            self.download(oid)
        except FileNotFoundError:
            self.upload(oid, io.BytesIO(data))
        return oid

    def smudge(self, oid: str) -> bytes:
        with self.download(oid) as fh:
            return fh.read()


__all__ = ["S3FSFilter"]
