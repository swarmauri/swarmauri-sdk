from typing import Any, Literal

from pydantic import Field, model_validator
from swarmauri_base.model_providers.ModelProviderBase import ModelProviderBase

from .OpenAIAuthConfig import OpenAIAuthConfig
from .OpenAIEndpoints import OpenAIEndpoints
from .OpenAIErrorMapper import OpenAIErrorMapper
from .OpenAIModelCatalog import OpenAIModelCatalog


class OpenAIProvider(ModelProviderBase):
    provider_name: Literal["openai"] = "openai"
    endpoints: OpenAIEndpoints = Field(default_factory=OpenAIEndpoints)
    auth: OpenAIAuthConfig = Field(
        default_factory=OpenAIAuthConfig, exclude=True
    )
    catalog: OpenAIModelCatalog = Field(default_factory=OpenAIModelCatalog)
    error_mapper: OpenAIErrorMapper = Field(default_factory=OpenAIErrorMapper)
    type: Literal["OpenAIProvider"] = "OpenAIProvider"

    @model_validator(mode="after")
    def configure(self) -> "OpenAIProvider":
        self.base_url = self.base_url or self.endpoints.resolve("api")
        self.endpoints.base_url = self.base_url
        if self.api_key is not None:
            self.auth.api_key = self.api_key
        elif self.auth.api_key is not None:
            self.api_key = self.auth.api_key
        if self.organization is not None:
            self.auth.organization = self.organization
        elif self.auth.organization is not None:
            self.organization = self.auth.organization
        if self.project is not None:
            self.auth.project = self.project
        elif self.auth.project is not None:
            self.project = self.auth.project
        if self.organization:
            self.default_headers.setdefault(
                "OpenAI-Organization", self.organization
            )
        if self.project:
            self.default_headers.setdefault("OpenAI-Project", self.project)
        return self

    def connection_options(self) -> dict[str, Any]:
        options = super().connection_options()
        if self.api_key is not None:
            options["api_key"] = self.api_key.get_secret_value()
        return options
