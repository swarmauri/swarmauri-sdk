import io
import json
import pytest

from swarmauri_transport_stdio.StdioTransport import StdioTransport


@pytest.fixture
def stdio_transport():
    in_stream = io.StringIO()
    out_stream = io.StringIO()
    transport = StdioTransport(in_stream=in_stream, out_stream=out_stream)
    return transport, in_stream, out_stream


@pytest.mark.timeout(5)
@pytest.mark.unit
def test_ubc_resource(stdio_transport):
    transport, _, _ = stdio_transport
    assert transport.resource == "Transport"


@pytest.mark.timeout(5)
@pytest.mark.unit
def test_ubc_type(stdio_transport):
    transport, _, _ = stdio_transport
    assert transport.type == "StdioTransport"


@pytest.mark.timeout(5)
@pytest.mark.unit
@pytest.mark.asyncio
async def test_send_writes_output(stdio_transport):
    transport, _, out_stream = stdio_transport
    await transport.send({"sender": "alice", "recipient": "bob", "message": {"msg": "hello"}})
    out_stream.seek(0)
    payload = json.loads(out_stream.readline())
    assert payload == {"sender": "alice", "recipient": "bob", "message": {"msg": "hello"}}


@pytest.mark.timeout(5)
@pytest.mark.unit
@pytest.mark.asyncio
async def test_receive_reads_input(stdio_transport):
    transport, in_stream, _ = stdio_transport
    in_stream.write(json.dumps({"sender": "bob", "recipient": "alice", "message": "hi"}) + "\n")
    in_stream.seek(0)
    data = await transport.recv()
    assert data == {"sender": "bob", "recipient": "alice", "message": "hi"}
