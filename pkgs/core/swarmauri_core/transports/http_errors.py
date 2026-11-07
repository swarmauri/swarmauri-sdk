"""Transport-neutral HTTP exceptions."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .i_http_response import IHttpResponse


class HttpTransportError(Exception):
    """Base error for HTTP transport operations."""


class HttpRequestError(HttpTransportError):
    """A request failed before a usable response was received."""


class HttpStatusError(HttpTransportError):
    """An HTTP response reported an unsuccessful status code."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        response: IHttpResponse,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response = response
