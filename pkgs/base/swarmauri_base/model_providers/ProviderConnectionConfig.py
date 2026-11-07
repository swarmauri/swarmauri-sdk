"""Resolved connection data passed from a provider to a transport."""

from typing import Any, Literal

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
