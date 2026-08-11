from typing import Any, Literal

from pydantic import Field, model_validator
from swarmauri_base.model_providers.ModelProviderBase import ModelProviderBase
from swarmauri_base.model_providers.ProviderConnectionConfigBase import (
    ProviderConnectionConfigBase,
)

from .OpenRouterAuthConfig import OpenRouterAuthConfig
from .OpenRouterEndpoints import OpenRouterEndpoints
from .OpenRouterErrorMapper import OpenRouterErrorMapper
from .OpenRouterModelCatalog import OpenRouterModelCatalog


class OpenRouterProvider(ModelProviderBase):
    provider_name: Literal["openrouter"] = "openrouter"
    endpoints: OpenRouterEndpoints = Field(default_factory=OpenRouterEndpoints)
    catalog: OpenRouterModelCatalog = Field(
        default_factory=OpenRouterModelCatalog
    )
    error_mapper: OpenRouterErrorMapper = Field(
        default_factory=OpenRouterErrorMapper
    )
    auth: OpenRouterAuthConfig = Field(
        default_factory=OpenRouterAuthConfig, exclude=True
    )
    site_url: str | None = None
    app_name: str | None = None
    type: Literal["OpenRouterProvider"] = "OpenRouterProvider"

    @model_validator(mode="after")
    def configure(self) -> "OpenRouterProvider":
        self.base_url = self.base_url or self.endpoints.base_url
        self.endpoints.base_url = self.base_url
        if self.api_key is not None:
            self.auth.api_key = self.api_key
        elif self.auth.api_key is not None:
            self.api_key = self.auth.api_key
        if self.site_url is not None:
            self.auth.site_url = self.site_url
        elif self.auth.site_url is not None:
            self.site_url = self.auth.site_url
        if self.app_name is not None:
            self.auth.app_name = self.app_name
        elif self.auth.app_name is not None:
            self.app_name = self.auth.app_name
        return self

    def connection_config(
        self,
        capability: str,
        model: str | None = None,
    ) -> ProviderConnectionConfigBase:
        endpoints = {
            "chat.completions": self.endpoints.resolve(
                self.endpoints.chat_completions_path
            ),
            "models.list": self.endpoints.resolve(self.endpoints.models_path),
            "images.generate": self.endpoints.resolve(
                self.endpoints.image_generations_path
            ),
        }
        try:
            endpoint = endpoints[capability]
        except KeyError as error:
            raise ValueError(
                f"OpenRouter does not support capability {capability!r}"
            ) from error
        options: dict[str, Any] = super().connection_options()
        if model is not None:
            options["model"] = model
        return ProviderConnectionConfigBase(
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
    def authorize(config: ProviderConnectionConfigBase) -> dict[str, str]:
        auth = config.auth_context
        if not isinstance(auth, OpenRouterAuthConfig):
            raise TypeError(
                "OpenRouter connection configuration has no auth context"
            )
        return auth.apply(config.headers)
