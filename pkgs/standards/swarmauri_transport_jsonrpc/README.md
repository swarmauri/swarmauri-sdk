# Swarmauri JSON-RPC Transport

`JsonRpcTransport` enables JSON-RPC 2.0 message exchange over standard input and output streams.

## Usage

```python
from swarmauri_transport_jsonrpc import JsonRpcTransport
from peagen.transport.schemas import RPCRequest
import io

in_stream = io.StringIO()
out_stream = io.StringIO()
transport = JsonRpcTransport(in_stream=in_stream, out_stream=out_stream)
req = RPCRequest(method="ping", params={}, id=1)
await transport.send(req)
```
