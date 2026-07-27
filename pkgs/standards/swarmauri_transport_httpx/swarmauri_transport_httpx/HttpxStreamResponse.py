from collections.abc import Iterator
from typing import Any

from pydantic import PrivateAttr

from swarmauri_base.transports.http import HttpStreamResponseBase


class HttpxStreamResponse(HttpStreamResponseBase):
    _response: Any = PrivateAttr(default=None)

    @classmethod
    def from_response(cls, response: Any) -> "HttpxStreamResponse":
        result = cls(
            status_code=response.status_code,
            headers=dict(response.headers),
        )
        result._response = response
        return result

    def iter_bytes(self) -> Iterator[bytes]:
        yield from self._response.iter_bytes()

    def read(self) -> bytes:
        return self._response.read()

    def json(self) -> Any:
        return self._response.json()

    def raise_for_status(self) -> None:
        self._response.raise_for_status()
