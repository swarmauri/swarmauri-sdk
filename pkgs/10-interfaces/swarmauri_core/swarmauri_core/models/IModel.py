"""Common interface for model resources."""

from abc import ABC

from swarmauri_core.model_providers.IModelProvider import IModelProvider

from .IModelCapabilities import IModelCapabilities


class IModel(ABC):
    """Identity and capability shape shared by every model family."""

    name: str
    provider: IModelProvider | None
    capabilities: IModelCapabilities
