"""Common interface for model resources."""

from abc import ABC
from typing import Any
from .IModelCapabilities import IModelCapabilities


class IModel(ABC):
    """Identity and capability shape shared by every model family."""

    name: str
    provider: Any
    capabilities: IModelCapabilities
