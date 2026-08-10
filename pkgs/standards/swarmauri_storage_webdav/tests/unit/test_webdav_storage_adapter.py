from __future__ import annotations

import io
from importlib.metadata import entry_points, version
from pathlib import Path
import tomllib
from urllib.parse import unquote
from xml.sax.saxutils import escape

import httpx
import pytest

from swarmauri_storage_webdav import (
    WebDAVError,
    WebDAVLockedError,
    WebDAVStorageAdapter,
    __version__,
)


class WebDAVFixture:
    def __init__(self) -> None:
        self.collections = {"/dav/"}
        self.objects: dict[str, bytes] = {}
        self.requests: list[httpx.Request] = []

    @staticmethod
    def _collection_path(path: str) -> str:
        return path.rstrip("/") + "/"

    def _propfind(self, path: str) -> httpx.Response:
        collection = self._collection_path(path)
        if collection not in self.collections:
            return httpx.Response(404)

        resources: list[tuple[str, bool]] = [(collection, True)]
        for candidate in sorted(self.collections):
            if candidate == collection or not candidate.startswith(collection):
                continue
            remainder = candidate[len(collection) :].strip("/")
            if remainder and "/" not in remainder:
                resources.append((candidate, True))
        for candidate in sorted(self.objects):
            if not candidate.startswith(collection):
                continue
            remainder = candidate[len(collection) :]
            if remainder and "/" not in remainder:
                resources.append((candidate, False))

        responses = []
        for href, is_collection in resources:
            resource_type = "<D:collection/>" if is_collection else ""
            responses.append(
                "<D:response>"
                f"<D:href>{escape(href)}</D:href>"
                "<D:propstat><D:prop>"
                f"<D:resourcetype>{resource_type}</D:resourcetype>"
                "</D:prop><D:status>HTTP/1.1 200 OK</D:status>"
                "</D:propstat></D:response>"
            )
        body = (
            '<?xml version="1.0" encoding="utf-8"?>'
            '<D:multistatus xmlns:D="DAV:">'
            + "".join(responses)
            + "</D:multistatus>"
        )
        return httpx.Response(
            207,
            content=body.encode(),
            headers={"Content-Type": "application/xml"},
        )

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        path = unquote(request.url.path)

        if path.endswith("locked.txt"):
            return httpx.Response(423)
        if request.method == "OPTIONS":
            return httpx.Response(200, headers={"DAV": "1, extended-mkcol"})
        if request.method == "MKCOL":
            collection = self._collection_path(path)
            if collection in self.collections:
                return httpx.Response(405)
            self.collections.add(collection)
            return httpx.Response(201)
        if request.method == "PUT":
            self.objects[path] = request.content
            return httpx.Response(201)
        if request.method == "GET":
            if path not in self.objects:
                return httpx.Response(404)
            payload = self.objects[path]
            range_header = request.headers.get("Range")
            if range_header:
                bounds = range_header.removeprefix("bytes=").split("-")
                start, end = int(bounds[0]), int(bounds[1])
                if start >= len(payload):
                    return httpx.Response(416)
                return httpx.Response(206, content=payload[start : end + 1])
            return httpx.Response(200, content=payload)
        if request.method == "DELETE":
            if path not in self.objects:
                return httpx.Response(404)
            del self.objects[path]
            return httpx.Response(204)
        if request.method == "PROPFIND":
            return self._propfind(path)
        if request.method in {"COPY", "MOVE"}:
            if path not in self.objects:
                return httpx.Response(404)
            destination = unquote(
                urlsplit_header(request.headers["Destination"])
            )
            self.objects[destination] = self.objects[path]
            if request.method == "MOVE":
                del self.objects[path]
            return httpx.Response(201)
        return httpx.Response(405)


def urlsplit_header(value: str) -> str:
    return httpx.URL(value).path


@pytest.fixture
def server() -> WebDAVFixture:
    return WebDAVFixture()


@pytest.fixture
def adapter(server: WebDAVFixture) -> WebDAVStorageAdapter:
    client = httpx.Client(transport=httpx.MockTransport(server))
    return WebDAVStorageAdapter(
        base_url="https://dav.example.test/dav/",
        prefix="artifacts",
        client=client,
    )


def test_resource_type_and_serialization(
    adapter: WebDAVStorageAdapter,
    server: WebDAVFixture,
) -> None:
    assert adapter.resource == "StorageAdapter"
    assert adapter.type == "WebDAVStorageAdapter"

    restored = WebDAVStorageAdapter(
        base_url="https://dav.example.test/dav/",
        client=httpx.Client(transport=httpx.MockTransport(server)),
        **adapter.model_dump(),
    )
    assert restored.type == adapter.type


def test_version_metadata() -> None:
    assert __version__ == version("swarmauri_storage_webdav")


def test_capabilities(adapter: WebDAVStorageAdapter) -> None:
    assert adapter.capabilities() == {"1", "extended-mkcol"}


def test_upload_download_and_url_encoding(
    adapter: WebDAVStorageAdapter,
) -> None:
    uri = adapter.upload("runs/hello world.txt", io.BytesIO(b"payload"))

    assert uri.endswith("/artifacts/runs/hello%20world.txt")
    assert adapter.download("runs/hello world.txt").read() == b"payload"


def test_upload_rejects_path_traversal(
    adapter: WebDAVStorageAdapter,
) -> None:
    with pytest.raises(ValueError, match="unsafe storage key"):
        adapter.upload("../escape.txt", io.BytesIO(b"payload"))


def test_iter_prefix_uses_bounded_propfind(
    adapter: WebDAVStorageAdapter,
    server: WebDAVFixture,
) -> None:
    adapter.upload("runs/one.txt", io.BytesIO(b"one"))
    adapter.upload("runs/nested/two.txt", io.BytesIO(b"two"))

    assert sorted(adapter.iter_prefix("runs")) == [
        "runs/nested/two.txt",
        "runs/one.txt",
    ]
    propfinds = [
        request for request in server.requests if request.method == "PROPFIND"
    ]
    assert propfinds
    assert all(request.headers["Depth"] == "1" for request in propfinds)


def test_push_and_pull(
    adapter: WebDAVStorageAdapter,
    tmp_path: Path,
) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "nested").mkdir()
    (source / "nested" / "data.bin").write_bytes(b"data")

    adapter.push(source, prefix="release")
    destination = tmp_path / "destination"
    adapter.pull("release", destination)

    assert (destination / "nested" / "data.bin").read_bytes() == b"data"


@pytest.mark.asyncio
async def test_async_bytes_range_and_remove(
    adapter: WebDAVStorageAdapter,
) -> None:
    await adapter.put_bytes("range.bin", b"abcdef", "application/octet-stream")

    assert await adapter.get_bytes("range.bin") == b"abcdef"
    assert await adapter.get_range("range.bin", 2, 3) == b"cde"

    await adapter.remove_object("range.bin")
    with pytest.raises(FileNotFoundError):
        await adapter.get_bytes("range.bin")


def test_copy_and_move(
    adapter: WebDAVStorageAdapter,
) -> None:
    adapter.put_blob("source.txt", b"source")

    adapter.copy("source.txt", "copies/copied.txt")
    assert adapter.get_blob("copies/copied.txt") == b"source"

    adapter.move("copies/copied.txt", "moved.txt")
    assert adapter.get_blob("moved.txt") == b"source"
    with pytest.raises(FileNotFoundError):
        adapter.get_blob("copies/copied.txt")


def test_locked_response_has_specific_exception(
    adapter: WebDAVStorageAdapter,
) -> None:
    with pytest.raises(WebDAVLockedError):
        adapter.download("locked.txt")


def test_multistatus_rejects_entity_declarations(
    adapter: WebDAVStorageAdapter,
) -> None:
    payload = b'<!DOCTYPE x [<!ENTITY secret "unsafe">]><multistatus />'

    with pytest.raises(WebDAVError, match="unsafe XML declaration"):
        adapter._parse_multistatus(payload)


def test_from_uri_removes_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    clients: list[dict] = []

    class DummyClient:
        def __init__(self, **kwargs) -> None:
            clients.append(kwargs)

        def close(self) -> None:
            return None

    monkeypatch.setattr(
        "swarmauri_storage_webdav.webdav_storage_adapter.httpx.Client",
        DummyClient,
    )

    created = WebDAVStorageAdapter.from_uri(
        "webdav+https://user:p%40ss@dav.example.test/root/"
    )

    assert created.root_uri == "https://dav.example.test/root/"
    assert "user" not in created.root_uri
    assert isinstance(clients[0]["auth"], httpx.BasicAuth)


def test_invalid_auth_combinations(server: WebDAVFixture) -> None:
    client = httpx.Client(transport=httpx.MockTransport(server))
    with pytest.raises(ValueError, match="bearer_token"):
        WebDAVStorageAdapter(
            base_url="https://dav.example.test/dav/",
            username="user",
            bearer_token="token",
            client=client,
        )


def test_storage_entry_points_declared() -> None:
    data = tomllib.loads(Path("pyproject.toml").read_text())
    target = (
        "swarmauri_storage_webdav.webdav_storage_adapter:WebDAVStorageAdapter"
    )

    assert (
        data["project"]["entry-points"]["swarmauri.storage_adapters"][
            "WebDAVStorageAdapter"
        ]
        == target
    )
    assert (
        data["project"]["entry-points"]["peagen.plugins.storage_adapters"][
            "webdav"
        ]
        == target
    )


def test_storage_entry_point_is_discoverable() -> None:
    matches = {
        item.name: item
        for item in entry_points(group="swarmauri.storage_adapters")
    }

    assert matches["WebDAVStorageAdapter"].load() is WebDAVStorageAdapter
