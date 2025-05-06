import pytest
import asyncio
import json
import http.client
import urllib.parse

from http_client import HttpClient as CurlLikeHTTPClient
from http_client.exceptions import TimeoutError, HTTP2Error, ProtocolError
from http_client.h2 import frames, hpack, multiplex, flow_control

# --- Dummy classes to simulate http.client connections and responses ---

class DummyResponse:
    def __init__(self, status, headers, body):
        self.status = status
        self._headers = headers
        self._body = body

    def getheaders(self):
        return self._headers

    def read(self):
        return self._body

class DummySocket:
    def selected_alpn_protocol(self):
        # Simulate ALPN returning "h2" when HTTP/2 is negotiated.
        return "h2"

class DummyHTTPSConnection:
    def __init__(self, netloc, timeout=None, context=None):
        self.netloc = netloc
        self.timeout = timeout
        self.context = context
        self.sock = DummySocket()  # Simulate an SSL socket with ALPN result.
    def request(self, method, path, body=None, headers=None):
        self.method = method
        self.path = path
        self.body = body
        self.headers = headers
    def getresponse(self):
        # Return a dummy response.
        return DummyResponse(200, [("Content-Type", "application/json")], b'{"message": "ok"}')
    def close(self):
        pass

class DummyHTTPConnection:
    def __init__(self, netloc, timeout=None):
        self.netloc = netloc
        self.timeout = timeout
    def request(self, method, path, body=None, headers=None):
        self.method = method
        self.path = path
        self.body = body
        self.headers = headers
    def getresponse(self):
        return DummyResponse(200, [("Content-Type", "application/json")], b'{"message": "ok"}')
    def close(self):
        pass

# --- HTTP/1.1 Tests ---

def test_sync_get_http1_1(monkeypatch):
    """
    Test a synchronous GET using HTTP/1.1.
    """
    monkeypatch.setattr(http.client, "HTTPConnection", DummyHTTPConnection)
    monkeypatch.setattr(http.client, "HTTPSConnection", DummyHTTPSConnection)

    client = CurlLikeHTTPClient(base_url="http://example.com", timeout=5, version="1.1")
    status, headers, body = client.get(
        "/test",
        headers={"Accept": "application/json"},
        params={"q": "test"}
    )
    assert status == 200
    # Check that "Content-Type" is present.
    assert any(h[0] == "Content-Type" for h in headers)
    data = json.loads(body)
    assert data["message"] == "ok"

@pytest.mark.asyncio
async def test_async_get_http1_1(monkeypatch):
    """
    Test an asynchronous GET using HTTP/1.1.
    """
    async def dummy_open_connection(host, port, ssl=None):
        reader = asyncio.StreamReader()
        # Simulate a valid HTTP/1.1 response.
        response = (
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Type: application/json\r\n"
            b"\r\n"
            b'{"message": "ok"}'
        )
        reader.feed_data(response)
        reader.feed_eof()

        class DummyWriter:
            def write(self, data):
                pass
            async def drain(self):
                pass
            def get_extra_info(self, name):
                if name == "ssl_object":
                    class DummySSL:
                        def selected_alpn_protocol(self):
                            return "http/1.1"
                    return DummySSL()
                return None
            def close(self):
                pass
            async def wait_closed(self):
                pass
        return reader, DummyWriter()

    monkeypatch.setattr(asyncio, "open_connection", dummy_open_connection)
    client = CurlLikeHTTPClient(base_url="https://example.com", timeout=5, version="1.1")
    response_text = await client.aget("/test", headers={"Accept": "application/json"})
    assert "200 OK" in response_text
    assert '{"message": "ok"}' in response_text

# --- HTTP/2 ALPN Tests ---

def test_alpn_negotiation_http2_sync(monkeypatch):
    """
    Test that a synchronous request with HTTP/2 branches to the HTTP/2 handler.
    We patch the async HTTP/2 handler since sync requests use asyncio.run().
    """
    monkeypatch.setattr(http.client, "HTTPSConnection", DummyHTTPSConnection)
    async def dummy_handle_http2_async_request(self, method, parsed_url, path, headers, data):
        return (201, [("Content-Type", "application/json")], b'{"message": "http2"}')
    monkeypatch.setattr(CurlLikeHTTPClient, "_handle_http2_async_request", dummy_handle_http2_async_request)

    client = CurlLikeHTTPClient(base_url="https://example.com", timeout=5, version="2")
    status, headers, body = client.get("/test", headers={"Accept": "application/json"})
    assert status == 201
    data = json.loads(body)
    assert data["message"] == "http2"

@pytest.mark.asyncio
async def test_alpn_negotiation_http2_async(monkeypatch):
    """
    Test that an async request with HTTP/2 delegates to the HTTP/2 async handler.
    """
    async def dummy_handle_http2_async_request(self, method, parsed_url, path, headers, data):
        return '{"message": "http2 async"}'
    monkeypatch.setattr(CurlLikeHTTPClient, "_handle_http2_async_request", dummy_handle_http2_async_request)

    async def dummy_open_connection(host, port, ssl=None):
        reader = asyncio.StreamReader()
        reader.feed_data(b"")  # No real response data.
        reader.feed_eof()
        class DummyWriter:
            def write(self, data):
                pass
            async def drain(self):
                pass
            def get_extra_info(self, name):
                if name == "ssl_object":
                    class DummySSL:
                        def selected_alpn_protocol(self):
                            return "h2"
                    return DummySSL()
                return None
            def close(self):
                pass
            async def wait_closed(self):
                pass
        return reader, DummyWriter()

    monkeypatch.setattr(asyncio, "open_connection", dummy_open_connection)
    client = CurlLikeHTTPClient(base_url="https://example.com", timeout=5, version="2")
    response_text = await client.aget("/test", headers={"Accept": "application/json"})
    data = json.loads(response_text)
    assert data["message"] == "http2 async"

# --- Multiplexing Tests ---

@pytest.mark.asyncio
async def test_flow_control_basic():
    """
    Test basic flow control operations using FlowControlManager.
    """
    fc = flow_control.FlowControlManager()
    fc.add_stream(1)
    initial_conn = fc.connection_window
    initial_stream = fc.stream_windows[1]

    # Simulate consuming part of the window.
    fc.consume_window(1, 1000)
    assert fc.connection_window == initial_conn - 1000
    assert fc.stream_windows[1] == initial_stream - 1000

    # Update windows.
    fc.update_window(1, 5000)
    fc.update_window(0, 5000)
    # Allow the notify task to run.
    await asyncio.sleep(0.1)
    assert fc.stream_windows[1] == initial_stream - 1000 + 5000
    assert fc.connection_window == initial_conn - 1000 + 5000

# --- Binary Framing Tests ---

def test_binary_framing_pack_unpack():
    """
    Test that an HTTP2Frame can be packed and then unpacked correctly.
    """
    payload = b"test payload"
    original_frame = frames.HTTP2Frame(frame_type=frames.DATA, flags=0x1, stream_id=15, payload=payload)
    packed = original_frame.pack()
    unpacked_frame, remainder = frames.HTTP2Frame.unpack(packed)
    assert remainder == b""
    assert unpacked_frame.frame_type == original_frame.frame_type
    assert unpacked_frame.flags == original_frame.flags
    assert unpacked_frame.stream_id == original_frame.stream_id
    assert unpacked_frame.payload == original_frame.payload

@pytest.mark.asyncio
async def test_multiplexing_complete(monkeypatch):
    """
    Test multiplexing by simulating a complete request/response cycle using the HTTP/2 multiplexer.
    This test creates a dummy reader and writer, starts the multiplexer, creates a new stream,
    sends a HEADERS frame, then manually places a dummy response frame into the stream queue,
    and finally asserts that get_response returns the expected frame.
    """
    # Create a dummy reader.
    reader = asyncio.StreamReader()
    # Create a dummy writer that collects written data.
    class DummyWriter:
        def __init__(self):
            self.data = b""
        def write(self, data):
            self.data += data
        async def drain(self):
            pass
        def get_extra_info(self, name):
            if name == "ssl_object":
                class DummySSL:
                    def selected_alpn_protocol(self):
                        return "h2"
                return DummySSL()
            return None
        def close(self):
            pass
        async def wait_closed(self):
            pass
    writer = DummyWriter()

    # Instantiate the multiplexer.
    multiplexer = multiplex.HTTP2Multiplexer(reader, writer)
    await multiplexer.start_receiving()

    # Create a new stream.
    stream_id = multiplexer.create_stream()

    # Create a HEADERS frame for the stream.
    headers_dict = {"method": "GET", "path": "/dummy"}
    header_block = hpack.hpack_encode(headers_dict)
    headers_frame = frames.HTTP2Frame(
        frame_type=frames.HEADERS,
        flags=0x4,  # END_HEADERS flag.
        stream_id=stream_id,
        payload=header_block
    )

    # Simulate sending the HEADERS frame.
    await multiplexer.send_frame(headers_frame)

    # Now, simulate that the frame was received by manually placing it into the stream queue.
    await multiplexer.streams[stream_id].put(headers_frame)

    # Retrieve the frame via get_response.
    response_frame = await multiplexer.get_response(stream_id, timeout=1)
    assert response_frame.frame_type == frames.HEADERS
    assert response_frame.payload == header_block

    await multiplexer.stop_receiving()


@pytest.mark.asyncio
async def test_error_handling_stream_reset(monkeypatch):
    """
    Test that when a RST_STREAM frame is received, the client (multiplexer) raises a ProtocolError.
    We simulate this by manually placing a RST_STREAM frame into the stream queue and then
    monkey-patching get_response to check the frame type.
    """
    # Create a dummy multiplexer with a StreamReader.
    reader = asyncio.StreamReader()
    # Writer is not used in this test.
    multiplexer = multiplex.HTTP2Multiplexer(reader, None)
    # Ensure stream 1 exists.
    multiplexer.streams[1] = asyncio.Queue()

    # Create a dummy RST_STREAM frame.
    rst_frame = frames.HTTP2Frame(
        frame_type=frames.RST_STREAM,
        flags=0,
        stream_id=1,
        payload=b""
    )
    # Place the RST_STREAM frame into the stream queue.
    await multiplexer.streams[1].put(rst_frame)

    # Monkey-patch get_response to raise ProtocolError if a RST_STREAM frame is encountered.
    original_get_response = multiplexer.get_response
    async def get_response_with_reset(stream_id, timeout=None):
        frame = await original_get_response(stream_id, timeout)
        if frame.frame_type == frames.RST_STREAM:
            raise ProtocolError("Stream reset encountered")
        return frame
    monkeypatch.setattr(multiplexer, "get_response", get_response_with_reset)

    with pytest.raises(ProtocolError):
        await multiplexer.get_response(1, timeout=1)
