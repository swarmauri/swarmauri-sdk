from typing import Any, Literal

from pydantic import Field, model_validator
from swarmauri_base.model_providers.ModelProviderBase import ModelProviderBase

from .XAIEndpoints import XAIEndpoints
from .XAIErrorMapper import XAIErrorMapper
from .XAIModelCatalog import XAIModelCatalog


class XAIProvider(ModelProviderBase):
    provider_name: Literal["xai"] = "xai"
    endpoints: XAIEndpoints = Field(default_factory=XAIEndpoints)
    catalog: XAIModelCatalog = Field(default_factory=XAIModelCatalog)
    error_mapper: XAIErrorMapper = Field(default_factory=XAIErrorMapper)
    type: Literal["XAIProvider"] = "XAIProvider"

    @model_validator(mode="after")
    def configure(self) -> "XAIProvider":
        self.base_url = self.base_url or self.endpoints.base_url
        return self

    def connection_options(self) -> dict[str, Any]:
        options = super().connection_options()
        if self.api_key:
            options["api_key"] = self.api_key.get_secret_value()
        return options
