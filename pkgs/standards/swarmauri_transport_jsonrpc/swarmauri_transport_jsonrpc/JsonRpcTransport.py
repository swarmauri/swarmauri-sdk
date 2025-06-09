from __future__ import annotations

import json
import sys
from typing import Any, TextIO, Literal

from pydantic import PrivateAttr

from swarmauri_base.transports.TransportBase import TransportBase, TransportProtocol
from swarmauri_base.ComponentBase import ComponentBase
from peagen.transport.schemas import RPCRequest, RPCResponse


@ComponentBase.register_type(TransportBase, "JsonRpcTransport")
class JsonRpcTransport(TransportBase):
    """Exchange JSON-RPC 2.0 messages over standard streams."""

    _in_stream: TextIO = PrivateAttr()
    _out_stream: TextIO = PrivateAttr()

    type: Literal["JsonRpcTransport"] = "JsonRpcTransport"
    allowed_protocols: list[TransportProtocol] = [TransportProtocol.UNICAST]

    def __init__(self, in_stream: TextIO | None = None, out_stream: TextIO | None = None, **kwargs):
        super().__init__(**kwargs)
        self._in_stream = in_stream or sys.stdin
        self._out_stream = out_stream or sys.stdout

    def _send_request(self, request: RPCRequest) -> None:
        self._out_stream.write(request.model_dump_json() + "\n")
        self._out_stream.flush()

    def _send_response(self, response: RPCResponse) -> None:
        self._out_stream.write(response.model_dump_json() + "\n")
        self._out_stream.flush()

    async def send(self, msg: Any, **meta: Any) -> None:
        """Send an RPC request or response."""
        if isinstance(msg, RPCRequest):
            self._send_request(msg)
        elif isinstance(msg, RPCResponse):
            self._send_response(msg)
        elif isinstance(msg, dict) and ("method" in msg or "result" in msg or "error" in msg):
            if "method" in msg:
                self._send_request(RPCRequest.model_validate(msg))
            else:
                self._send_response(RPCResponse.model_validate(msg))
        else:
            raise ValueError("msg must be RPCRequest or RPCResponse data")

    async def recv(self, **opts: Any) -> RPCRequest | RPCResponse:
        """Receive an RPC request or response."""
        line = self._in_stream.readline()
        if not line:
            raise EOFError("No input available")
        payload = json.loads(line)
        if "method" in payload:
            return RPCRequest.model_validate(payload)
        return RPCResponse.model_validate(payload)
