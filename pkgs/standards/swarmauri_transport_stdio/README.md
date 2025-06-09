# Swarmauri Stdio Transport

This package provides `StdioTransport`, a simple transport that exchanges JSON messages over standard input and output streams.

## Usage

```python
from swarmauri_transport_stdio import StdioTransport
import io

in_stream = io.StringIO()
out_stream = io.StringIO()
transport = StdioTransport(in_stream=in_stream, out_stream=out_stream)
await transport.send({"sender": "alice", "recipient": "bob", "message": {"hello": "world"}})
```
