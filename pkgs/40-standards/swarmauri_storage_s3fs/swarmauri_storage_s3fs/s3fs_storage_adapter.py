"""S3 storage adapter backed strictly by the :mod:`s3fs` filesystem API."""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import BinaryIO, Literal

import s3fs
from pydantic import SecretStr

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.storage import StorageAdapterBase


@ComponentBase.register_type(StorageAdapterBase, "S3FSStorageAdapter")
class S3FSStorageAdapter(StorageAdapterBase):
    """Store and retrieve artifacts from S3 through ``s3fs.S3FileSystem``."""

    type: Literal["S3FSStorageAdapter"] = "S3FSStorageAdapter"

    def __init__(
        self,
        bucket: str,
        *,
        key: SecretStr | str | None = None,
        secret: SecretStr | str | None = None,
        token: SecretStr | str | None = None,
        endpoint_url: str | None = None,
        region_name: str | None = None,
        use_ssl: bool = True,
        anon: bool = False,
        prefix: str = "",
        client_kwargs: dict | None = None,
        config_kwargs: dict | None = None,
        s3_additional_kwargs: dict | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._bucket = bucket
        self._prefix = self.normalize_prefix(prefix)

        fs_client_kwargs = dict(client_kwargs or {})
        if endpoint_url:
            fs_client_kwargs["endpoint_url"] = endpoint_url
        if region_name:
            fs_client_kwargs["region_name"] = region_name

        self._fs = s3fs.S3FileSystem(
            key=self._secret_value(key),
            secret=self._secret_value(secret),
            token=self._secret_value(token),
            endpoint_url=endpoint_url,
            use_ssl=use_ssl,
            anon=anon,
            client_kwargs=fs_client_kwargs or None,
            config_kwargs=config_kwargs,
            s3_additional_kwargs=s3_additional_kwargs,
        )

    @staticmethod
    def _secret_value(value: SecretStr | str | None) -> str | None:
        if isinstance(value, SecretStr):
            return value.get_secret_value() or None
        return value or None

    def _full_key(self, key: str) -> str:
        key = self.compose_key(self._prefix, key, allow_empty=True)
        return f"{self._bucket}/{key}" if key else self._bucket

    def _relative_key(self, path: str) -> str:
        rel = path.removeprefix(f"{self._bucket}/")
        if self._prefix and rel.startswith(f"{self._prefix.rstrip('/')}/"):
            rel = rel[len(self._prefix.rstrip("/")) + 1 :]
        return rel

    @property
    def root_uri(self) -> str:
        """Return the base ``s3://`` URI for this adapter."""
        base = f"s3://{self._bucket}"
        uri = f"{base}/{self._prefix.rstrip('/')}" if self._prefix else base
        return uri.rstrip("/") + "/"

    def upload(self, key: str, data: BinaryIO) -> str:
        """Upload *data* under *key* and return its ``s3://`` URI."""
        normalized_key = self.normalize_key(key)
        with self._fs.open(self._full_key(key), "wb") as handle:
            shutil.copyfileobj(data, handle)
        return f"{self.root_uri}{normalized_key}"

    def download(self, key: str) -> BinaryIO:
        """Open *key* for binary reads."""
        try:
            return self._fs.open(self._full_key(key), "rb")
        except FileNotFoundError:
            raise
        except OSError as exc:
            raise FileNotFoundError(key) from exc

    def upload_dir(self, src: str | os.PathLike, *, prefix: str = "") -> None:
        """Recursively upload files from *src* under ``prefix``."""
        base = Path(src)
        for path in base.rglob("*"):
            if path.is_file():
                rel = path.relative_to(base).as_posix()
                key = self.compose_key(prefix, rel)
                with path.open("rb") as handle:
                    self.upload(key, handle)

    def iter_prefix(self, prefix: str):
        """Yield stored keys below ``prefix`` relative to the adapter root."""
        for path in self._fs.find(self._full_key(prefix)):
            rel = self._relative_key(path)
            if rel:
                yield rel

    def download_dir(self, prefix: str, dest_dir: str | os.PathLike) -> None:
        """Download all stored artifacts under ``prefix`` into ``dest_dir``."""
        dest = Path(dest_dir)
        normalized_prefix = self.normalize_prefix(prefix)
        for rel_key in self.iter_prefix(prefix):
            target_rel = rel_key
            if normalized_prefix and rel_key.startswith(
                f"{normalized_prefix}/"
            ):
                target_rel = rel_key[len(normalized_prefix) + 1 :]
            if not target_rel:
                continue
            target = self.download_target_for_key(dest, target_rel)
            target.parent.mkdir(parents=True, exist_ok=True)
            data = self.download(rel_key)
            with target.open("wb") as handle:
                shutil.copyfileobj(data, handle)

    async def ensure_bucket(self) -> None:
        """Create the configured bucket if it does not already exist."""
        if not self._fs.exists(self._bucket):
            self._fs.mkdir(self._bucket)

    async def get_range(
        self, object_key: str, start: int, length: int
    ) -> bytes:
        """Retrieve a byte range using the ``s3fs`` file object."""
        info = self._fs.info(self._full_key(object_key))
        parsed_start, parsed_end = self._parse_range(
            start, length, info["size"]
        )
        with self._fs.open(self._full_key(object_key), "rb") as handle:
            handle.seek(parsed_start)
            return handle.read(parsed_end - parsed_start)

    async def remove_object(self, object_key: str) -> None:
        """Delete ``object_key`` when it exists."""
        path = self._full_key(object_key)
        if self._fs.exists(path):
            self._fs.rm(path)

    @classmethod
    def from_uri(cls, uri: str) -> "S3FSStorageAdapter":
        """Instantiate the adapter from an ``s3://bucket/prefix`` URI."""
        from urllib.parse import urlparse

        parsed = urlparse(uri)
        if parsed.scheme != "s3":
            raise ValueError("URI must start with s3://")

        return cls(
            bucket=parsed.netloc,
            prefix=parsed.path.lstrip("/"),
            key=os.getenv("AWS_ACCESS_KEY_ID"),
            secret=os.getenv("AWS_SECRET_ACCESS_KEY"),
            token=os.getenv("AWS_SESSION_TOKEN"),
            endpoint_url=os.getenv("AWS_ENDPOINT_URL"),
            region_name=os.getenv("AWS_REGION"),
        )
