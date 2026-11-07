"""Common model-provider behavior."""

from typing import Any, Literal

from pydantic import ConfigDict, Field, SecretStr
from swarmauri_core.model_providers.IModelProvider import IModelProvider

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes

from .ModelCatalogBase import ModelCatalogBase
from .ProviderAuthBase import ProviderAuthBase
from .ProviderConnectionConfig import ProviderConnectionConfig
from .ProviderEndpointBase import ProviderEndpointBase
from .ProviderErrorMapperBase import ProviderErrorMapperBase


@ComponentBase.register_model()
class ModelProviderBase(IModelProvider, ComponentBase):
    provider_name: str = ""
    base_url: str | None = None
    api_key: SecretStr | None = Field(default=None, exclude=True)
    organization: str | None = None
    project: str | None = None
    region: str | None = None
    default_headers: dict[str, str] = Field(default_factory=dict)
    endpoints: ProviderEndpointBase = Field(
        default_factory=ProviderEndpointBase
    )
    auth: ProviderAuthBase = Field(
        default_factory=ProviderAuthBase, exclude=True
    )
    catalog: ModelCatalogBase = Field(default_factory=ModelCatalogBase)
    error_mapper: ProviderErrorMapperBase = Field(
        default_factory=ProviderErrorMapperBase
    )
    timeout: float = Field(default=600.0, gt=0)
    max_retries: int = Field(default=3, ge=0)
    options: dict[str, Any] = Field(default_factory=dict)
    resource: str = Field(
        default=ResourceTypes.MODEL_PROVIDER.value, frozen=True
    )
    type: Literal["ModelProviderBase"] = "ModelProviderBase"
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    def connection_options(self) -> dict[str, Any]:
        options = dict(self.options)
        options.setdefault("timeout", self.timeout)
        options.setdefault("max_retries", self.max_retries)
        return options

    def connection_config(
        self,
        capability: str,
        model: str | None = None,
    ) -> ProviderConnectionConfig:
        endpoint = self.endpoints.resolve(capability)
        return ProviderConnectionConfig(
            endpoint=endpoint,
            headers=dict(self.default_headers),
            # Call the base implementation deliberately. Some legacy concrete
            # providers still expose credentials from connection_options(); a
            # serializable connection DTO must keep them in auth_context only.
            transport_options=ModelProviderBase.connection_options(self),
            auth_context=self.auth,
        )

    @staticmethod
    def authorize(config: ProviderConnectionConfig) -> dict[str, str]:
        auth = config.auth_context
        if not isinstance(auth, ProviderAuthBase):
            raise TypeError(
                "Provider connection configuration has no auth context"
            )
        return dict(auth.apply(config.headers))
