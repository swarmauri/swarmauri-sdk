from __future__ import annotations

from swarmauri_core.transports.i_http_client import IHttpClient


class HttpClientMixin(IHttpClient):
    """Compatibility interface mixin for HTTP client transports."""
