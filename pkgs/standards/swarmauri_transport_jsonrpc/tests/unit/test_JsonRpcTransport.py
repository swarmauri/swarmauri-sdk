import io
from peagen.transport.schemas import RPCRequest, RPCResponse
from swarmauri_transport_jsonrpc import JsonRpcTransport
import pytest


@pytest.mark.asyncio
async def test_send_and_receive_request():
    in_stream = io.StringIO()
    out_stream = io.StringIO()
    transport = JsonRpcTransport(in_stream=in_stream, out_stream=out_stream)
    req = RPCRequest(method="echo", params={"msg": "hi"}, id=1)
    await transport.send(req)
    out_stream.seek(0)
    in_stream.write(out_stream.read())
    in_stream.seek(0)
    received = await transport.recv()
    assert isinstance(received, RPCRequest)
    assert received.method == "echo"


@pytest.mark.asyncio
async def test_send_response():
    out_stream = io.StringIO()
    transport = JsonRpcTransport(out_stream=out_stream, in_stream=io.StringIO())
    resp = RPCResponse(id=1, result="pong")
    await transport.send(resp)
    out_stream.seek(0)
    data = out_stream.readline().strip()
    assert data
