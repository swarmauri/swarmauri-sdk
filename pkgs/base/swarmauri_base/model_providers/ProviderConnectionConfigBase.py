from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ProviderConnectionConfigBase(BaseModel):
    endpoint: str | None = None
    headers: dict[str, str] = Field(default_factory=dict)
    query: dict[str, str] = Field(default_factory=dict)
    transport_options: dict[str, Any] = Field(default_factory=dict)
    auth_context: Any = Field(default=None, exclude=True)
    type: Literal["ProviderConnectionConfigBase"] = (
        "ProviderConnectionConfigBase"
    )
    model_config = ConfigDict(arbitrary_types_allowed=True)
