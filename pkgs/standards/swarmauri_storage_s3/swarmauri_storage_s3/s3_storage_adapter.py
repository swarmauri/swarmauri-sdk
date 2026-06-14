"""Generic S3-compatible storage adapter using direct S3 client semantics."""

from __future__ import annotations

import io
import os
import shutil
from pathlib import Path
from typing import BinaryIO, Literal

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from pydantic import SecretStr

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.storage import StorageAdapterBase


@ComponentBase.register_type(StorageAdapterBase, "S3StorageAdapter")
class S3StorageAdapter(StorageAdapterBase):
    """Store and retrieve artifacts through an S3-compatible API endpoint."""

    type: Literal["S3StorageAdapter"] = "S3StorageAdapter"

    def __init__(
        self,
        bucket: str,
        *,
        endpoint_url: str | None = None,
        region_name: str | None = None,
        access_key: SecretStr | str | None = None,
        secret_key: SecretStr | str | None = None,
        session_token: SecretStr | str | None = None,
        use_ssl: bool = True,
        verify: bool | str | None = None,
        addressing_style: str | None = None,
        prefix: str = "",
        client_kwargs: dict | None = None,
        config_kwargs: dict | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._bucket = bucket
        self._prefix = self.normalize_prefix(prefix)

        config_options = dict(config_kwargs or {})
        if addressing_style:
            config_options.setdefault("s3", {})["addressing_style"] = addressing_style

        options = dict(client_kwargs or {})
        options.update(
            {
                "service_name": "s3",
                "endpoint_url": endpoint_url,
                "region_name": region_name,
                "aws_access_key_id": self._secret_value(access_key),
                "aws_secret_access_key": self._secret_value(secret_key),
                "aws_session_token": self._secret_value(session_token),
                "use_ssl": use_ssl,
                "verify": verify,
            }
        )
        options = {key: value for key, value in options.items() if value is not None}
        if config_options:
            options["config"] = Config(**config_options)

        self._client = boto3.client(**options)

    @staticmethod
    def _secret_value(value: SecretStr | str | None) -> str | None:
        if isinstance(value, SecretStr):
            return value.get_secret_value() or None
        return value or None

    def _full_key(self, key: str) -> str:
        return self.compose_key(self._prefix, key, allow_empty=True)

    def _relative_key(self, key: str) -> str:
        if self._prefix and key.startswith(f"{self._prefix.rstrip('/')}/"):
            return key[len(self._prefix.rstrip("/")) + 1 :]
        return key

    @property
    def root_uri(self) -> str:
        """Return the base ``s3://`` URI for this adapter."""
        base = f"s3://{self._bucket}"
        uri = f"{base}/{self._prefix.rstrip('/')}" if self._prefix else base
        return uri.rstrip("/") + "/"

    def upload(self, key: str, data: BinaryIO) -> str:
        """Upload *data* under *key* and return its ``s3://`` URI."""
        normalized_key = self.normalize_key(key)
        self._client.upload_fileobj(data, self._bucket, self._full_key(key))
        return f"{self.root_uri}{normalized_key}"

    def download(self, key: str) -> BinaryIO:
        """Download *key* into a binary in-memory stream."""
        buffer = io.BytesIO()
        try:
            self._client.download_fileobj(self._bucket, self._full_key(key), buffer)
        except ClientError as exc:
            if self._is_missing(exc):
                raise FileNotFoundError(key) from exc
            raise
        buffer.seek(0)
        return buffer

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
        continuation_token = None
        list_prefix = self._full_key(self.normalize_prefix(prefix))
        while True:
            request = {
                "Bucket": self._bucket,
                "Prefix": list_prefix,
            }
            if continuation_token:
                request["ContinuationToken"] = continuation_token
            response = self._client.list_objects_v2(**request)
            for item in response.get("Contents", []):
                rel = self._relative_key(item["Key"])
                if rel:
                    yield rel
            if not response.get("IsTruncated"):
                break
            continuation_token = response.get("NextContinuationToken")

    def download_dir(self, prefix: str, dest_dir: str | os.PathLike) -> None:
        """Download all stored artifacts under ``prefix`` into ``dest_dir``."""
        dest = Path(dest_dir)
        normalized_prefix = self.normalize_prefix(prefix)
        for rel_key in self.iter_prefix(prefix):
            target_rel = rel_key
            if normalized_prefix and rel_key.startswith(f"{normalized_prefix}/"):
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
        try:
            self._client.head_bucket(Bucket=self._bucket)
        except ClientError as exc:
            if self._is_missing(exc):
                self._client.create_bucket(Bucket=self._bucket)
                return
            raise

    async def put_bytes(self, object_key: str, data: bytes, content_type: str) -> None:
        """Store raw bytes under *object_key* with an explicit content type."""
        self._client.put_object(
            Bucket=self._bucket,
            Key=self._full_key(object_key),
            Body=data,
            ContentType=content_type,
        )

    async def get_bytes(self, object_key: str) -> bytes:
        """Retrieve the stored object as bytes."""
        try:
            response = self._client.get_object(
                Bucket=self._bucket,
                Key=self._full_key(object_key),
            )
        except ClientError as exc:
            if self._is_missing(exc):
                raise FileNotFoundError(object_key) from exc
            raise
        return response["Body"].read()

    async def get_range(self, object_key: str, start: int, length: int) -> bytes:
        """Retrieve a byte range using S3 range requests."""
        try:
            head = self._client.head_object(
                Bucket=self._bucket,
                Key=self._full_key(object_key),
            )
        except ClientError as exc:
            if self._is_missing(exc):
                raise FileNotFoundError(object_key) from exc
            raise
        parsed_start, parsed_end = self._parse_range(
            start, length, head["ContentLength"]
        )
        response = self._client.get_object(
            Bucket=self._bucket,
            Key=self._full_key(object_key),
            Range=f"bytes={parsed_start}-{parsed_end - 1}",
        )
        return response["Body"].read()

    async def remove_object(self, object_key: str) -> None:
        """Delete ``object_key`` when it exists."""
        self._client.delete_object(Bucket=self._bucket, Key=self._full_key(object_key))

    @staticmethod
    def _is_missing(exc: ClientError) -> bool:
        code = exc.response.get("Error", {}).get("Code", "")
        return code in {"404", "NoSuchKey", "NoSuchBucket", "NotFound"}

    @classmethod
    def from_uri(cls, uri: str) -> "S3StorageAdapter":
        """Instantiate the adapter from an ``s3://bucket/prefix`` URI."""
        from urllib.parse import urlparse

        parsed = urlparse(uri)
        if parsed.scheme != "s3":
            raise ValueError("URI must start with s3://")

        return cls(
            bucket=parsed.netloc,
            prefix=parsed.path.lstrip("/"),
            endpoint_url=os.getenv("AWS_ENDPOINT_URL"),
            region_name=os.getenv("AWS_REGION"),
            access_key=os.getenv("AWS_ACCESS_KEY_ID"),
            secret_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            session_token=os.getenv("AWS_SESSION_TOKEN"),
        )
