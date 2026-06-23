"""S3-style object storage adapter backed by SFTP."""

from __future__ import annotations

import io
import os
import posixpath
import shutil
from pathlib import Path
from typing import BinaryIO, Literal
from urllib.parse import parse_qs, unquote, urlparse

import paramiko
from pydantic import SecretStr

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.storage import StorageAdapterBase


@ComponentBase.register_type(StorageAdapterBase, "S3OverSftpStorageAdapter")
class S3OverSftpStorageAdapter(StorageAdapterBase):
    """Persist S3-like bucket objects below a remote SFTP directory."""

    type: Literal["S3OverSftpStorageAdapter"] = "S3OverSftpStorageAdapter"

    def __init__(
        self,
        bucket: str,
        *,
        host: str | None = None,
        port: int = 22,
        username: str | None = None,
        password: SecretStr | str | None = None,
        key_filename: str | os.PathLike | None = None,
        root_dir: str = ".",
        prefix: str = "",
        transport: paramiko.Transport | None = None,
        sftp_client: paramiko.SFTPClient | None = None,
        connect_kwargs: dict | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._bucket = self.normalize_key(bucket)
        self._prefix = self.normalize_prefix(prefix)
        self._host = host
        self._port = port
        self._username = username
        self._password = self._secret_value(password)
        self._key_filename = str(key_filename) if key_filename is not None else None
        self._root_dir = self._normalize_remote_root(root_dir)
        self._owns_connection = transport is None and sftp_client is None
        self._owns_sftp = sftp_client is None
        self._transport = transport
        self._ssh_client: paramiko.SSHClient | None = None
        self._sftp = sftp_client or self._open_sftp(connect_kwargs or {})

    @staticmethod
    def _secret_value(value: SecretStr | str | None) -> str | None:
        if isinstance(value, SecretStr):
            return value.get_secret_value() or None
        return value or None

    @staticmethod
    def _normalize_remote_root(root_dir: str) -> str:
        root = posixpath.normpath(root_dir or ".")
        return "" if root == "." else root.rstrip("/")

    def _open_sftp(self, connect_kwargs: dict) -> paramiko.SFTPClient:
        if self._transport is not None:
            return paramiko.SFTPClient.from_transport(self._transport)
        if self._host is None:
            raise ValueError(
                "host is required unless transport or sftp_client is provided"
            )

        self._ssh_client = paramiko.SSHClient()
        self._ssh_client.load_system_host_keys()
        options = dict(connect_kwargs)
        options.setdefault("hostname", self._host)
        options.setdefault("port", self._port)
        options.setdefault("username", self._username)
        options.setdefault("password", self._password)
        if self._key_filename is not None:
            options.setdefault("key_filename", self._key_filename)
        self._ssh_client.connect(
            **{key: value for key, value in options.items() if value is not None}
        )
        return self._ssh_client.open_sftp()

    def close(self) -> None:
        """Close owned SFTP resources."""
        if self._owns_sftp:
            self._sftp.close()
        if self._owns_connection and self._ssh_client is not None:
            self._ssh_client.close()
        if self._owns_connection and self._transport is not None:
            self._transport.close()

    def _remote_join(self, *parts: str, allow_empty: bool = False) -> str:
        key = self.compose_key(*parts, allow_empty=allow_empty)
        path_parts = [part for part in (self._root_dir, key) if part]
        return posixpath.join(*path_parts) if path_parts else "."

    def _bucket_key(self, key: str, *, allow_empty: bool = False) -> str:
        return self.compose_key(
            self._bucket, self._prefix, key, allow_empty=allow_empty
        )

    def _remote_path(self, key: str, *, allow_empty: bool = False) -> str:
        return self._remote_join(self._bucket_key(key, allow_empty=allow_empty))

    def _relative_key(self, remote_path: str) -> str:
        base = self._remote_path("", allow_empty=True).rstrip("/")
        rel = (
            remote_path[len(base) :].lstrip("/")
            if base and remote_path.startswith(base)
            else remote_path
        )
        return self.normalize_key(rel, allow_empty=True)

    @staticmethod
    def _is_missing(exc: OSError) -> bool:
        return getattr(exc, "errno", None) == 2 or "No such file" in str(exc)

    def _mkdir_p(self, remote_dir: str) -> None:
        if remote_dir in {"", ".", "/"}:
            return
        parts = remote_dir.strip("/").split("/")
        path = "/" if remote_dir.startswith("/") else ""
        for part in parts:
            path = posixpath.join(path, part) if path else part
            try:
                self._sftp.stat(path)
            except OSError as exc:
                if not self._is_missing(exc):
                    raise
                self._sftp.mkdir(path)

    @property
    def root_uri(self) -> str:
        """Return the base ``s3+sftp://`` URI for this adapter."""
        auth = ""
        if self._username:
            auth = f"{self._username}@"
        host = self._host or "sftp"
        port = f":{self._port}" if self._port != 22 else ""
        key = self.compose_key(self._bucket, self._prefix, allow_empty=True)
        return f"s3+sftp://{auth}{host}{port}/{key.rstrip('/')}/"

    def upload(self, key: str, data: BinaryIO) -> str:
        """Upload *data* under *key* and return its object URI."""
        normalized_key = self.normalize_key(key)
        remote_path = self._remote_path(key)
        self._mkdir_p(posixpath.dirname(remote_path))
        with self._sftp.open(remote_path, "wb") as target:
            shutil.copyfileobj(data, target)
        return f"{self.root_uri}{normalized_key}"

    def download(self, key: str) -> BinaryIO:
        """Download *key* into an in-memory binary stream."""
        buffer = io.BytesIO()
        try:
            with self._sftp.open(self._remote_path(key), "rb") as source:
                shutil.copyfileobj(source, buffer)
        except OSError as exc:
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
        remote_prefix = self._remote_path(
            self.normalize_prefix(prefix), allow_empty=True
        )
        try:
            for remote_path in self._walk(remote_prefix):
                rel = self._relative_key(remote_path)
                if rel:
                    yield rel
        except OSError as exc:
            if self._is_missing(exc):
                return
            raise

    def _walk(self, remote_dir: str):
        for entry in self._sftp.listdir_attr(remote_dir):
            remote_path = posixpath.join(remote_dir, entry.filename)
            if self._is_directory(entry):
                yield from self._walk(remote_path)
            else:
                yield remote_path

    @staticmethod
    def _is_directory(entry) -> bool:
        import stat

        return stat.S_ISDIR(entry.st_mode)

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
        """Create the bucket directory when it does not already exist."""
        self._mkdir_p(self._remote_join(self._bucket))

    async def put_bytes(self, object_key: str, data: bytes, content_type: str) -> None:
        """Store raw bytes under *object_key*."""
        del content_type
        self.upload(object_key, io.BytesIO(data))

    async def get_bytes(self, object_key: str) -> bytes:
        """Retrieve the stored object as bytes."""
        return self.get_blob(object_key)

    async def get_range(self, object_key: str, start: int, length: int) -> bytes:
        """Retrieve a byte range from the remote object."""
        remote_path = self._remote_path(object_key)
        try:
            size = self._sftp.stat(remote_path).st_size
            parsed_start, parsed_end = self._parse_range(start, length, size)
            with self._sftp.open(remote_path, "rb") as source:
                source.seek(parsed_start)
                return source.read(parsed_end - parsed_start)
        except OSError as exc:
            if self._is_missing(exc):
                raise FileNotFoundError(object_key) from exc
            raise

    async def remove_object(self, object_key: str) -> None:
        """Delete ``object_key`` when it exists."""
        try:
            self._sftp.remove(self._remote_path(object_key))
        except OSError as exc:
            if not self._is_missing(exc):
                raise

    @classmethod
    def from_uri(cls, uri: str) -> "S3OverSftpStorageAdapter":
        """Instantiate the adapter from an ``s3+sftp://`` URI."""
        parsed = urlparse(uri)
        if parsed.scheme != "s3+sftp":
            raise ValueError("URI must start with s3+sftp://")

        path_parts = [unquote(part) for part in parsed.path.split("/") if part]
        if not path_parts:
            raise ValueError("URI path must include a bucket")

        query = parse_qs(parsed.query)
        root_dir = query.get("root_dir", ["."])[0]
        return cls(
            bucket=path_parts[0],
            prefix="/".join(path_parts[1:]),
            host=parsed.hostname,
            port=parsed.port or 22,
            username=unquote(parsed.username) if parsed.username else None,
            password=unquote(parsed.password) if parsed.password else None,
            root_dir=root_dir,
        )
