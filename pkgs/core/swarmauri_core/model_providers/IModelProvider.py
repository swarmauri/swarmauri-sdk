"""Model provider interface."""

from abc import ABC, abstractmethod
from typing import Any, Mapping, Optional

from .IModelCatalog import IModelCatalog
from .IProviderErrorMapper import IProviderErrorMapper


class IModelProvider(ABC):
    provider_name: str
    base_url: str | None
    default_headers: Mapping[str, str]
    catalog: IModelCatalog
    error_mapper: IProviderErrorMapper

    @abstractmethod
    def connection_options(self) -> Mapping[str, Any]: ...

    @abstractmethod
    def connection_config(
        self,
        capability: str,
        model: str | None = None,
    ) -> Any: ...
