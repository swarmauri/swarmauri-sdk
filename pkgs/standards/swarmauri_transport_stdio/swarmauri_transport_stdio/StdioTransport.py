from __future__ import annotations

import json
import sys
from typing import Any, TextIO, Literal

from pydantic import PrivateAttr

from swarmauri_base.transports.TransportBase import TransportBase, TransportProtocol
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(TransportBase, "StdioTransport")
class StdioTransport(TransportBase):
    """Transport messages over standard input and output."""

    _in_stream: TextIO = PrivateAttr()
    _out_stream: TextIO = PrivateAttr()

    type: Literal["StdioTransport"] = "StdioTransport"
    allowed_protocols: list[TransportProtocol] = [TransportProtocol.UNICAST]

    def __init__(self, in_stream: TextIO | None = None, out_stream: TextIO | None = None, **kwargs):
        super().__init__(**kwargs)
        self._in_stream = in_stream or sys.stdin
        self._out_stream = out_stream or sys.stdout

    async def send(self, msg: Any, **meta: Any) -> None:
        """Serialize ``msg`` to JSON and write it to the output stream."""
        self._out_stream.write(json.dumps(msg) + "\n")
        self._out_stream.flush()

    async def recv(self, **opts: Any) -> Any:
        """Read a JSON message from the input stream."""
        line = self._in_stream.readline()
        if not line:
            raise EOFError("No input available")
        return json.loads(line)
