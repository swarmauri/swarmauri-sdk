"""Shared HTTP client configuration."""

from abc import ABC

from pydantic import ConfigDict, Field
from swarmauri_core.transports.i_http_client import IHttpClient

from swarmauri_base.ComponentBase import ComponentBase


class HttpClientBase(IHttpClient, ComponentBase, ABC):
    base_url: str | None = None
    default_headers: dict[str, str] = Field(default_factory=dict)
    timeout: float = Field(default=60.0, gt=0)

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    def resolve_url(self, path: str) -> str:
        if path.startswith(("http://", "https://")):
            return path
        if not self.base_url:
            return path
        return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"

    def merge_headers(
        self, headers: dict[str, str] | None
    ) -> dict[str, str]:
        merged = dict(self.default_headers)
        merged.update(headers or {})
        return merged
