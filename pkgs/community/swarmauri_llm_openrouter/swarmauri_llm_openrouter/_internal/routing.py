"""Define provider-routing preferences supported by OpenRouter."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


class OpenRouterProviderPreferences(BaseModel):
    """Configure OpenRouter provider selection and data handling."""

    order: list[str] | None = None
    allow_fallbacks: bool = True
    require_parameters: bool = False
    data_collection: Literal["allow", "deny"] | None = None
    zdr: bool | None = None
    options: dict[str, Any] | None = None
    model_config = ConfigDict(extra="forbid")
