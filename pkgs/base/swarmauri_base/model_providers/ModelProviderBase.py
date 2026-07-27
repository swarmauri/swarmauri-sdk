"""Common model-provider behavior."""

from typing import Any, Literal

from pydantic import ConfigDict, Field, SecretStr
from swarmauri_core.model_providers.IModelProvider import IModelProvider

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes

from .ModelCatalogBase import ModelCatalogBase
from .ProviderConnectionConfigBase import ProviderConnectionConfigBase
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
    ) -> ProviderConnectionConfigBase:
        return ProviderConnectionConfigBase(
            endpoint=self.base_url,
            headers=dict(self.default_headers),
            transport_options=self.connection_options(),
        )
