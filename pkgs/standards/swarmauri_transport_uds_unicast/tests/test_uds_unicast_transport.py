import asyncio
from types import SimpleNamespace

import pytest

import swarmauri_core.transports as transports

transports.UnicastTransportMixin = type("UnicastTransportMixin", (), {})
transports.PeerTransportMixin = type("PeerTransportMixin", (), {})

from swarmauri_transport_uds_unicast import UdsUnicastTransport  # noqa: E402


def test_supports_declares_expected_capabilities() -> None:
    transport = UdsUnicastTransport("/tmp/example.sock")

    capabilities = transport.supports()

    assert {protocol.name for protocol in capabilities.protocols} == {"UDS"}
    assert capabilities.io.name == "STREAM"
    assert {cast.name for cast in capabilities.casts} == {"UNICAST"}
    assert {feature.name for feature in capabilities.features} == {
        "RELIABLE",
        "ORDERED",
        "LOCAL_ONLY",
    }
    assert capabilities.security.name == "NONE"
    assert {scheme.name for scheme in capabilities.schemes} == {"UDS"}


@pytest.mark.asyncio
async def test_send_writes_to_connected_writer() -> None:
    sent = bytearray()

    class StubWriter:
        def write(self, data: bytes) -> None:
            sent.extend(data)

        async def drain(self) -> None:
            pass

    transport = UdsUnicastTransport("/tmp/example.sock")
    transport._writer = StubWriter()  # type: ignore[attr-defined]

    await transport.send("peer", b"payload")

    assert sent == b"payload"


@pytest.mark.asyncio
async def test_recv_returns_bytes() -> None:
    class StubReader:
        async def read(self, n: int) -> bytes:  # noqa: ARG002
            return b"response"

    transport = UdsUnicastTransport("/tmp/example.sock")
    transport._reader = StubReader()  # type: ignore[attr-defined]

    data = await transport.recv()

    assert data == b"response"


@pytest.mark.asyncio
async def test_start_server_unlinks_existing_socket(monkeypatch, tmp_path) -> None:
    path = tmp_path / "uds.sock"
    path.write_text("stale")
    captured = {}

    async def fake_start_unix_server(callback, *, path: str):  # noqa: ARG001
        captured["path"] = path
        return SimpleNamespace(close=lambda: None, wait_closed=lambda: asyncio.sleep(0))

    transport = UdsUnicastTransport(str(path))
    monkeypatch.setattr(asyncio, "start_unix_server", fake_start_unix_server)

    await transport._start_server()

    assert captured["path"] == str(path)
    assert not path.exists()
    assert transport._server is not None  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_stop_server_closes_and_unlinks(tmp_path) -> None:
    path = tmp_path / "uds.sock"
    path.write_text("socket")
    closed = False
    waited = False

    async def wait_closed() -> None:
        nonlocal waited
        waited = True

    def close() -> None:
        nonlocal closed
        closed = True

    transport = UdsUnicastTransport(str(path))
    transport._server = SimpleNamespace(close=close, wait_closed=wait_closed)  # type: ignore[attr-defined]

    await transport._stop_server()

    assert closed and waited
    assert not path.exists()
    assert transport._server is None  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_open_client_sets_streams(monkeypatch, tmp_path) -> None:
    path = tmp_path / "uds.sock"
    reader = object()
    writer = object()

    async def fake_open_unix_connection(path_arg: str):  # noqa: ARG001
        return reader, writer

    transport = UdsUnicastTransport(str(path))
    monkeypatch.setattr(asyncio, "open_unix_connection", fake_open_unix_connection)

    await transport._open_client()

    assert transport._reader is reader  # type: ignore[attr-defined]
    assert transport._writer is writer  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_send_without_connection_raises(tmp_path) -> None:
    transport = UdsUnicastTransport(str(tmp_path / "uds.sock"))

    with pytest.raises(RuntimeError, match="not connected"):
        await transport.send("peer", b"data")


@pytest.mark.asyncio
async def test_recv_without_connection_raises(tmp_path) -> None:
    transport = UdsUnicastTransport(str(tmp_path / "uds.sock"))

    with pytest.raises(RuntimeError, match="not connected"):
        await transport.recv()


@pytest.mark.asyncio
async def test_accept_without_server_started(tmp_path) -> None:
    transport = UdsUnicastTransport(str(tmp_path / "uds.sock"))

    with pytest.raises(RuntimeError, match="server not started"):
        await transport.accept()


@pytest.mark.asyncio
async def test_stop_server_without_socket_path(tmp_path) -> None:
    path = tmp_path / "uds.sock"
    transport = UdsUnicastTransport(str(path))

    await transport._stop_server()

    assert not path.exists()
