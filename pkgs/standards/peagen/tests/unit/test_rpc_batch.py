import pytest
from peagen.transport import RPCDispatcher


@pytest.mark.unit
@pytest.mark.asyncio
async def test_rpc_batch_dispatch():
    rpc = RPCDispatcher()

    @rpc.method("echo")
    async def echo(value):
        return value

    req = [
        {"jsonrpc": "2.0", "id": 1, "method": "echo", "params": {"value": "a"}},
        {"jsonrpc": "2.0", "id": 2, "method": "echo", "params": {"value": "b"}},
    ]
    resp = await rpc.dispatch(req)
    assert [r["result"] for r in resp] == ["a", "b"]
