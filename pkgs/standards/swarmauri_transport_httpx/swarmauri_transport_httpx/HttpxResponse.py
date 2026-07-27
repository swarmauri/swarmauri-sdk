from __future__ import annotations

from typing import Any

from pydantic import PrivateAttr

from swarmauri_base.transports.http import HttpResponseBase


class HttpxResponse(HttpResponseBase):
    _response: Any = PrivateAttr(default=None)

    @classmethod
    def from_response(cls, response: Any) -> "HttpxResponse":
        result = cls(
            status_code=response.status_code,
            headers=dict(response.headers),
        )
        result._response = response
        result.set_content(response.content)
        return result

    def raise_for_status(self) -> None:
        self._response.raise_for_status()
