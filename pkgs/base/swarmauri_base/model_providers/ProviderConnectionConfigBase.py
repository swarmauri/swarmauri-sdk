from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class ProviderConnectionConfigBase(BaseModel):
    endpoint: Optional[str] = None
    headers: Dict[str, str] = Field(default_factory=dict)
    query: Dict[str, str] = Field(default_factory=dict)
    transport_options: Dict[str, Any] = Field(default_factory=dict)
    auth_context: Any = Field(default=None, exclude=True)
    type: Literal["ProviderConnectionConfigBase"] = (
        "ProviderConnectionConfigBase"
    )
    model_config = ConfigDict(arbitrary_types_allowed=True)
