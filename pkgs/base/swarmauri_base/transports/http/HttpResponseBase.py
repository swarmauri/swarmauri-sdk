"""Reusable buffered HTTP response behavior."""

import json
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from swarmauri_core.transports.i_http_response import IHttpResponse


class HttpResponseBase(IHttpResponse, BaseModel):
    status_code: int
    headers: Dict[str, str] = Field(default_factory=dict)
    _content: bytes = PrivateAttr(default=b"")

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def set_content(self, content: bytes) -> None:
        self._content = content

    def read(self) -> bytes:
        return self._content

    async def aread(self) -> bytes:
        return self.read()

    def json(self) -> Any:
        return json.loads(self._content)

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP request failed: {self.status_code}")
