from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from .i_http_client import IHttpClient


class HttpClientMixin(IHttpClient, BaseModel):
    """Pydantic mixin for HTTP client transports."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="ignore")
