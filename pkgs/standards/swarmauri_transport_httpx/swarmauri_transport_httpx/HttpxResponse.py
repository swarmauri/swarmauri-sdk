from __future__ import annotations

from typing import Any

import httpx
from pydantic import PrivateAttr
from swarmauri_base.transports.http.HttpResponseBase import HttpResponseBase
from swarmauri_core.transports.http_errors import HttpStatusError


class HttpxResponse(HttpResponseBase):
    _response: Any = PrivateAttr(default=None)

    @classmethod
    def from_response(cls, response: Any) -> HttpxResponse:
        result = cls(
            status_code=response.status_code,
            headers=dict(response.headers),
        )
        result._response = response
        result.set_content(response.content)
        return result

    def raise_for_status(self) -> None:
        try:
            self._response.raise_for_status()
        except httpx.HTTPStatusError as error:
            raise HttpStatusError(
                str(error),
                status_code=self.status_code,
                response=self,
            ) from error
