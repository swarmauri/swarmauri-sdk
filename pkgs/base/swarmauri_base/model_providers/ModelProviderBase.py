"""Common model-provider behavior."""

from typing import Any, Dict, Literal, Optional

from pydantic import ConfigDict, Field, SecretStr

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.model_providers.IModelProvider import IModelProvider

from .ModelCatalogBase import ModelCatalogBase
from .ProviderConnectionConfigBase import ProviderConnectionConfigBase
from .ProviderErrorMapperBase import ProviderErrorMapperBase


@ComponentBase.register_model()
class ModelProviderBase(IModelProvider, ComponentBase):
    provider_name: str = ""
    base_url: Optional[str] = None
    api_key: Optional[SecretStr] = Field(default=None, exclude=True)
    organization: Optional[str] = None
    project: Optional[str] = None
    region: Optional[str] = None
    default_headers: Dict[str, str] = Field(default_factory=dict)
    catalog: ModelCatalogBase = Field(default_factory=ModelCatalogBase)
    error_mapper: ProviderErrorMapperBase = Field(
        default_factory=ProviderErrorMapperBase
    )
    timeout: float = Field(default=600.0, gt=0)
    max_retries: int = Field(default=3, ge=0)
    options: Dict[str, Any] = Field(default_factory=dict)
    resource: str = Field(
        default=ResourceTypes.MODEL_PROVIDER.value, frozen=True
    )
    type: Literal["ModelProviderBase"] = "ModelProviderBase"
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    def connection_options(self) -> Dict[str, Any]:
        options = dict(self.options)
        options.setdefault("timeout", self.timeout)
        options.setdefault("max_retries", self.max_retries)
        return options

    def connection_config(
        self,
        capability: str,
        model: Optional[str] = None,
    ) -> ProviderConnectionConfigBase:
        return ProviderConnectionConfigBase(
            endpoint=self.base_url,
            headers=dict(self.default_headers),
            transport_options=self.connection_options(),
        )
