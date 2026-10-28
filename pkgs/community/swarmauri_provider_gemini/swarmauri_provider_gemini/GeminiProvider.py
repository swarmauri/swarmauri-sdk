from typing import Literal

from pydantic import Field, model_validator
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.model_providers.ModelProviderBase import ModelProviderBase
from swarmauri_base.model_providers.ProviderConnectionConfig import (
    ProviderConnectionConfig,
)

from .GeminiAuthConfig import GeminiAuthConfig
from .GeminiEndpoints import GeminiEndpoints
from .GeminiErrorMapper import GeminiErrorMapper
from .GeminiModelCatalog import GeminiModelCatalog


@ComponentBase.register_type(ModelProviderBase, "GeminiProvider")
class GeminiProvider(ModelProviderBase):
    provider_name: Literal["gemini"] = "gemini"
    endpoints: GeminiEndpoints = Field(default_factory=GeminiEndpoints)
    auth: GeminiAuthConfig = Field(
        default_factory=GeminiAuthConfig, exclude=True
    )
    catalog: GeminiModelCatalog = Field(default_factory=GeminiModelCatalog)
    error_mapper: GeminiErrorMapper = Field(default_factory=GeminiErrorMapper)
    type: Literal["GeminiProvider"] = "GeminiProvider"

    @model_validator(mode="after")
    def configure(self) -> "GeminiProvider":
        self.base_url = self.base_url or self.endpoints.resolve("api")
        self.endpoints.base_url = self.base_url
        if self.api_key is not None:
            self.auth.api_key = self.api_key
        elif self.auth.api_key is not None:
            self.api_key = self.auth.api_key
        return self

    def prepare_connection(
        self, capability: str, model: str | None = None
    ) -> ProviderConnectionConfig:
        if capability != "live.connect":
            return super().prepare_connection(capability, model)

        config = self.connection_config(capability, model)
        return config.model_copy(
            update={"query": dict(self.auth.apply_query(config.query))}
        )
