"""WebDAV-backed Swarmauri storage adapter."""

from __future__ import annotations

import asyncio
import io
import os
import shutil
from pathlib import Path, PurePosixPath
from typing import BinaryIO, Iterator, Literal
from urllib.parse import quote, unquote, urlsplit, urlunsplit
from xml.etree.ElementTree import Element, fromstring

import httpx
from pydantic import SecretStr

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.storage import StorageAdapterBase

from .exceptions import (
    WebDAVError,
    WebDAVInsufficientStorageError,
    WebDAVLockedError,
    WebDAVPreconditionError,
)


@ComponentBase.register_type(StorageAdapterBase, "WebDAVStorageAdapter")
class WebDAVStorageAdapter(StorageAdapterBase):
    """Store and retrieve artifacts through a WebDAV collection."""

    type: Literal["WebDAVStorageAdapter"] = "WebDAVStorageAdapter"

    def __init__(
        self,
        base_url: str,
        *,
        prefix: str = "",
        username: str | None = None,
        password: SecretStr | str | None = None,
        bearer_token: SecretStr | str | None = None,
        auth: httpx.Auth | None = None,
        verify: bool | str = True,
        cert: str | tuple[str, str] | None = None,
        timeout: float = 30.0,
        follow_redirects: bool = True,
        headers: dict[str, str] | None = None,
        client: httpx.Client | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        parsed = urlsplit(base_url)
        if parsed.scheme not in {"http", "https"}:
            raise ValueError("base_url must use http:// or https://")
        if parsed.username is not None or parsed.password is not None:
            raise ValueError("base_url must not contain credentials")
        if parsed.query or parsed.fragment:
            raise ValueError("base_url must not contain a query or fragment")

        self._base_url = base_url.rstrip("/") + "/"
        self._prefix = self.normalize_prefix(prefix)
        self._owns_client = client is None

        password_value = self._secret_value(password)
        bearer_value = self._secret_value(bearer_token)

        if auth is not None and (username or password_value or bearer_value):
            raise ValueError(
                "auth cannot be combined with username, password, "
                "or bearer_token"
            )
        if bearer_value and (username or password_value):
            raise ValueError(
                "bearer_token cannot be combined with username or password"
            )

        request_headers = dict(headers or {})
        if bearer_value:
            request_headers["Authorization"] = f"Bearer {bearer_value}"

        resolved_auth = auth
        if resolved_auth is None and username is not None:
            resolved_auth = httpx.BasicAuth(username, password_value or "")

        self._client = client or httpx.Client(
            auth=resolved_auth,
            verify=verify,
            cert=cert,
            timeout=timeout,
            follow_redirects=follow_redirects,
            headers=request_headers,
        )

    @staticmethod
    def _secret_value(value: SecretStr | str | None) -> str | None:
        if isinstance(value, SecretStr):
            return value.get_secret_value() or None
        return value or None

    def _full_key(self, key: str, *, allow_empty: bool = False) -> str:
        return self.compose_key(
            self._prefix,
            key,
            allow_empty=allow_empty,
        )

    def _url_for_full_key(
        self,
        full_key: str,
        *,
        collection: bool = False,
    ) -> str:
        normalized = self.normalize_key(full_key, allow_empty=True)
        encoded = "/".join(
            quote(part, safe="") for part in normalized.split("/") if part
        )
        url = self._base_url + encoded
        if collection and not url.endswith("/"):
            url += "/"
        return url

    def _url(self, key: str, *, collection: bool = False) -> str:
        return self._url_for_full_key(
            self._full_key(key, allow_empty=True),
            collection=collection,
        )

    @property
    def root_uri(self) -> str:
        """Return the configured WebDAV collection URI."""
        return self._url("", collection=True)

    def _raise_for_status(
        self,
        response: httpx.Response,
        *,
        key: str | None = None,
    ) -> None:
        status = response.status_code
        target = key or str(response.request.url)
        if status < 400:
            return
        if status == 404:
            raise FileNotFoundError(target)
        if status in {401, 403}:
            raise PermissionError(target)
        if status == 412:
            raise WebDAVPreconditionError(target)
        if status == 423:
            raise WebDAVLockedError(target)
        if status == 507:
            raise WebDAVInsufficientStorageError(target)
        raise WebDAVError(
            f"{response.request.method} {response.request.url} "
            f"returned HTTP {status}"
        )

    def capabilities(self) -> set[str]:
        """Return capabilities advertised by the WebDAV endpoint."""
        response = self._client.request("OPTIONS", self.root_uri)
        self._raise_for_status(response)
        return {
            capability.strip()
            for capability in response.headers.get("DAV", "").split(",")
            if capability.strip()
        }

    def _ensure_collection(self, full_key: str) -> None:
        """Create each missing collection beneath the endpoint root."""
        normalized = self.normalize_key(full_key, allow_empty=True)
        current: list[str] = []
        for part in PurePosixPath(normalized).parts:
            current.append(part)
            key = "/".join(current)
            response = self._client.request(
                "MKCOL",
                self._url_for_full_key(key, collection=True),
            )
            if response.status_code not in {201, 405}:
                self._raise_for_status(response, key=key)

    def mkdir(self, key: str, *, parents: bool = True) -> str:
        """Create a collection and return its URL."""
        full_key = self._full_key(key)
        if parents:
            self._ensure_collection(full_key)
        else:
            response = self._client.request(
                "MKCOL",
                self._url_for_full_key(full_key, collection=True),
            )
            if response.status_code not in {201, 405}:
                self._raise_for_status(response, key=key)
        return self._url_for_full_key(full_key, collection=True)

    def upload(self, key: str, data: BinaryIO) -> str:
        """Upload a stream with PUT and return its resource URL."""
        normalized_key = self.normalize_key(key)
        full_key = self._full_key(normalized_key)
        parent = str(PurePosixPath(full_key).parent)
        if parent != ".":
            self._ensure_collection(parent)
        response = self._client.put(
            self._url_for_full_key(full_key),
            content=data,
        )
        self._raise_for_status(response, key=key)
        return self._url_for_full_key(full_key)

    def download(self, key: str) -> BinaryIO:
        """Download a resource into a seekable binary stream."""
        normalized_key = self.normalize_key(key)
        response = self._client.get(self._url(normalized_key))
        self._raise_for_status(response, key=key)
        stream = io.BytesIO(response.content)
        stream.seek(0)
        return stream

    def _propfind(self, key: str, *, depth: int = 1) -> httpx.Response:
        body = b"""<?xml version="1.0" encoding="utf-8"?>
<propfind xmlns="DAV:">
  <prop>
    <resourcetype />
    <getcontentlength />
    <getcontenttype />
    <getetag />
    <getlastmodified />
  </prop>
</propfind>
"""
        response = self._client.request(
            "PROPFIND",
            self._url(key, collection=True),
            headers={
                "Depth": str(depth),
                "Content-Type": "application/xml; charset=utf-8",
            },
            content=body,
        )
        self._raise_for_status(response, key=key)
        return response

    def _relative_href(self, href: str) -> str:
        base_path = unquote(urlsplit(self._base_url).path).rstrip("/") + "/"
        href_path = unquote(urlsplit(href).path)
        if not href_path.startswith(base_path):
            raise WebDAVError(
                f"server returned href outside configured root: {href!r}"
            )

        full_key = href_path[len(base_path) :].strip("/")
        full_key = self.normalize_key(full_key, allow_empty=True)
        if not self._prefix:
            return full_key
        if full_key == self._prefix:
            return ""
        if not full_key.startswith(f"{self._prefix}/"):
            raise WebDAVError(
                f"server returned href outside configured prefix: {href!r}"
            )
        return full_key[len(self._prefix) + 1 :]

    def _children(self, key: str) -> list[tuple[str, bool]]:
        response = self._propfind(key, depth=1)
        root = self._parse_multistatus(response.content)
        requested = self.normalize_prefix(key)
        children: list[tuple[str, bool]] = []
        for item in root.findall(".//{DAV:}response"):
            href_node = item.find("{DAV:}href")
            if href_node is None or not href_node.text:
                continue
            relative_key = self._relative_href(href_node.text)
            if relative_key == requested:
                continue
            is_collection = (
                item.find(".//{DAV:}resourcetype/{DAV:}collection") is not None
            )
            children.append((relative_key, is_collection))
        return children

    @staticmethod
    def _parse_multistatus(payload: bytes) -> Element:
        """Parse DAV XML after rejecting declarations that define entities."""
        lowered = payload.lower()
        if b"<!doctype" in lowered or b"<!entity" in lowered:
            raise WebDAVError("unsafe XML declaration in WebDAV response")
        return fromstring(payload)

    def iter_prefix(self, prefix: str = "") -> Iterator[str]:
        """Yield file keys using recursive, bounded Depth: 1 requests."""
        pending = [self.normalize_prefix(prefix)]
        visited: set[str] = set()
        while pending:
            current = pending.pop()
            if current in visited:
                continue
            visited.add(current)
            for key, is_collection in self._children(current):
                if is_collection:
                    pending.append(key)
                else:
                    yield key

    def upload_dir(
        self,
        src: str | os.PathLike,
        *,
        prefix: str = "",
    ) -> None:
        """Recursively upload files beneath prefix."""
        base = Path(src)
        if not base.is_dir():
            raise NotADirectoryError(base)
        if prefix:
            self.mkdir(prefix, parents=True)
        for path in base.rglob("*"):
            if path.is_file():
                relative = path.relative_to(base).as_posix()
                key = self.compose_key(prefix, relative)
                with path.open("rb") as handle:
                    self.upload(key, handle)

    def download_dir(
        self,
        prefix: str,
        dest_dir: str | os.PathLike,
    ) -> None:
        """Recursively download files beneath prefix."""
        normalized_prefix = self.normalize_prefix(prefix)
        destination = Path(dest_dir)
        for key in self.iter_prefix(normalized_prefix):
            target_key = key
            if normalized_prefix and key.startswith(f"{normalized_prefix}/"):
                target_key = key[len(normalized_prefix) + 1 :]
            target = self.download_target_for_key(destination, target_key)
            target.parent.mkdir(parents=True, exist_ok=True)
            with self.download(key) as source, target.open("wb") as output:
                shutil.copyfileobj(source, output)

    async def ensure_bucket(self) -> None:
        """Ensure the configured prefix collection exists."""
        if self._prefix:
            await asyncio.to_thread(self._ensure_collection, self._prefix)
        else:
            await asyncio.to_thread(self.capabilities)

    async def put_bytes(
        self,
        object_key: str,
        data: bytes,
        content_type: str,
    ) -> None:
        """Store bytes without blocking the event loop."""
        normalized_key = self.normalize_key(object_key)
        full_key = self._full_key(normalized_key)
        parent = str(PurePosixPath(full_key).parent)
        if parent != ".":
            await asyncio.to_thread(self._ensure_collection, parent)

        def put() -> None:
            response = self._client.put(
                self._url_for_full_key(full_key),
                content=data,
                headers={"Content-Type": content_type},
            )
            self._raise_for_status(response, key=object_key)

        await asyncio.to_thread(put)

    async def get_bytes(self, object_key: str) -> bytes:
        """Retrieve bytes without blocking the event loop."""
        return await asyncio.to_thread(self.get_blob, object_key)

    async def get_range(
        self,
        object_key: str,
        start: int,
        length: int,
    ) -> bytes:
        """Retrieve a byte range with an HTTP Range request."""
        if start < 0:
            raise ValueError("start must be >= 0")
        if length <= 0:
            raise ValueError("length must be > 0")

        def fetch() -> bytes:
            response = self._client.get(
                self._url(object_key),
                headers={"Range": f"bytes={start}-{start + length - 1}"},
            )
            if response.status_code == 416:
                raise ValueError("range start out of bounds")
            self._raise_for_status(response, key=object_key)
            if response.status_code == 206:
                return response.content
            if start >= len(response.content):
                raise ValueError("range start out of bounds")
            return response.content[start : start + length]

        return await asyncio.to_thread(fetch)

    async def remove_object(self, object_key: str) -> None:
        """Delete a resource if it exists."""

        def remove() -> None:
            response = self._client.delete(self._url(object_key))
            if response.status_code != 404:
                self._raise_for_status(response, key=object_key)

        await asyncio.to_thread(remove)

    def _transfer(
        self,
        method: Literal["COPY", "MOVE"],
        source: str,
        destination: str,
        *,
        overwrite: bool,
    ) -> str:
        destination_key = self.normalize_key(destination)
        destination_full_key = self._full_key(destination_key)
        parent = str(PurePosixPath(destination_full_key).parent)
        if parent != ".":
            self._ensure_collection(parent)
        response = self._client.request(
            method,
            self._url(source),
            headers={
                "Destination": self._url_for_full_key(destination_full_key),
                "Overwrite": "T" if overwrite else "F",
            },
        )
        self._raise_for_status(response, key=source)
        return self._url_for_full_key(destination_full_key)

    def copy(
        self,
        source: str,
        destination: str,
        *,
        overwrite: bool = False,
    ) -> str:
        """Copy a resource server-side."""
        return self._transfer("COPY", source, destination, overwrite=overwrite)

    def move(
        self,
        source: str,
        destination: str,
        *,
        overwrite: bool = False,
    ) -> str:
        """Move a resource server-side."""
        return self._transfer("MOVE", source, destination, overwrite=overwrite)

    def close(self) -> None:
        """Close the internally managed HTTP client."""
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> WebDAVStorageAdapter:
        return self

    def __exit__(self, *exc_info) -> None:
        self.close()

    @classmethod
    def from_uri(cls, uri: str) -> WebDAVStorageAdapter:
        """Create an adapter from a webdav+http(s) URI."""
        parsed = urlsplit(uri)
        schemes = {
            "webdav+http": "http",
            "webdav+https": "https",
        }
        if parsed.scheme not in schemes:
            raise ValueError("URI must use webdav+http:// or webdav+https://")
        netloc = parsed.netloc.rsplit("@", 1)[-1]
        base_url = urlunsplit(
            (schemes[parsed.scheme], netloc, parsed.path, "", "")
        )
        return cls(
            base_url=base_url,
            username=unquote(parsed.username) if parsed.username else None,
            password=unquote(parsed.password) if parsed.password else None,
        )
