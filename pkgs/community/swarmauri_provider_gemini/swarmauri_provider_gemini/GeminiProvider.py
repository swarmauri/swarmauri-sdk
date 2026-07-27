from typing import Any, Literal

from pydantic import Field, model_validator
from swarmauri_base.model_providers.ModelProviderBase import ModelProviderBase

from .GeminiEndpoints import GeminiEndpoints
from .GeminiErrorMapper import GeminiErrorMapper
from .GeminiModelCatalog import GeminiModelCatalog


class GeminiProvider(ModelProviderBase):
    provider_name: Literal["gemini"] = "gemini"
    endpoints: GeminiEndpoints = Field(default_factory=GeminiEndpoints)
    catalog: GeminiModelCatalog = Field(default_factory=GeminiModelCatalog)
    error_mapper: GeminiErrorMapper = Field(default_factory=GeminiErrorMapper)
    type: Literal["GeminiProvider"] = "GeminiProvider"

    @model_validator(mode="after")
    def configure(self) -> "GeminiProvider":
        self.base_url = self.base_url or self.endpoints.base_url
        return self

    def connection_options(self) -> dict[str, Any]:
        options = super().connection_options()
        if self.api_key is not None:
            options["api_key"] = self.api_key.get_secret_value()
        return options
