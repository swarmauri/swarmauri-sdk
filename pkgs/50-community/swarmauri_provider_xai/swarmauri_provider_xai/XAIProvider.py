from typing import Literal

from pydantic import Field, model_validator
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.model_providers.ModelProviderBase import ModelProviderBase
from swarmauri_base.model_providers.ProviderConnectionConfig import (
    ProviderConnectionConfig,
)

from .XAIAuthConfig import XAIAuthConfig
from .XAIEndpoints import XAIEndpoints
from .XAIErrorMapper import XAIErrorMapper
from .XAIModelCatalog import XAIModelCatalog


@ComponentBase.register_type(ModelProviderBase, "XAIProvider")
class XAIProvider(ModelProviderBase):
    provider_name: Literal["xai"] = "xai"
    endpoints: XAIEndpoints = Field(default_factory=XAIEndpoints)
    catalog: XAIModelCatalog = Field(default_factory=XAIModelCatalog)
    error_mapper: XAIErrorMapper = Field(default_factory=XAIErrorMapper)
    auth: XAIAuthConfig = Field(default_factory=XAIAuthConfig, exclude=True)
    type: Literal["XAIProvider"] = "XAIProvider"

    @model_validator(mode="after")
    def configure(self) -> "XAIProvider":
        self.base_url = self.base_url or self.endpoints.base_url
        self.endpoints.base_url = self.base_url
        if self.api_key is not None:
            self.auth.api_key = self.api_key
        elif self.auth.api_key is not None:
            self.api_key = self.auth.api_key
        return self

    def connection_config(
        self,
        capability: str,
        model: str | None = None,
    ) -> ProviderConnectionConfig:
        endpoint = self.endpoints.resolve(capability)
        options = super().connection_options()
        if model is not None:
            options["model"] = model
        return ProviderConnectionConfig(
            endpoint=endpoint,
            headers={
                **self.default_headers,
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            transport_options=options,
            auth_context=self.auth,
        )

    @staticmethod
    def authorize(config: ProviderConnectionConfig) -> dict[str, str]:
        auth = config.auth_context
        if not isinstance(auth, XAIAuthConfig):
            raise TypeError("xAI connection configuration has no auth context")
        return auth.apply(config.headers)
