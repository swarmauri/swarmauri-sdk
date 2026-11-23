from __future__ import annotations

from pydantic import BaseModel
from swarmauri_core.transports.i_http_client import IHttpClient


class HttpClientMixin(IHttpClient, BaseModel):
    """Compatibility interface mixin for HTTP client transports."""
