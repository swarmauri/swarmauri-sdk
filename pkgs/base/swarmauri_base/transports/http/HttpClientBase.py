"""Shared HTTP client configuration."""

from abc import ABC
from typing import Dict, Optional

from pydantic import ConfigDict, Field

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_core.transports.i_http_client import IHttpClient


class HttpClientBase(IHttpClient, ComponentBase, ABC):
    base_url: Optional[str] = None
    default_headers: Dict[str, str] = Field(default_factory=dict)
    timeout: float = Field(default=60.0, gt=0)

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    def resolve_url(self, path: str) -> str:
        if path.startswith(("http://", "https://")):
            return path
        if not self.base_url:
            return path
        return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"

    def merge_headers(
        self, headers: Optional[Dict[str, str]]
    ) -> Dict[str, str]:
        merged = dict(self.default_headers)
        merged.update(headers or {})
        return merged
