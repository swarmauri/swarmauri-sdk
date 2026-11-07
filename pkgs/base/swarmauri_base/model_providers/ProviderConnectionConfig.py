"""Resolved connection data passed from a provider to a transport."""

from typing import Any, Literal
from urllib.parse import urlencode

from pydantic import BaseModel, ConfigDict, Field


class ProviderConnectionConfig(BaseModel):
    """Final value object for a provider connection attempt."""

    endpoint: str | None = None
    headers: dict[str, str] = Field(default_factory=dict)
    query: dict[str, str] = Field(default_factory=dict)
    transport_options: dict[str, Any] = Field(default_factory=dict)
    auth_context: Any = Field(default=None, exclude=True)
    type: Literal["ProviderConnectionConfig"] = "ProviderConnectionConfig"
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def resolved_url(self) -> str:
        """Return the endpoint with its encoded query string."""
        if self.endpoint is None:
            raise ValueError("Provider connection has no endpoint")
        if not self.query:
            return self.endpoint
        separator = "&" if "?" in self.endpoint else "?"
        return f"{self.endpoint}{separator}{urlencode(self.query)}"
