"""Model provider interfaces."""

from .IModelCatalog import IModelCatalog
from .IModelProvider import IModelProvider
from .IProviderAuth import IProviderAuth
from .IProviderEndpoint import IProviderEndpoint
from .IProviderErrorMapper import IProviderErrorMapper

__all__ = [
    "IModelCatalog",
    "IModelProvider",
    "IProviderAuth",
    "IProviderEndpoint",
    "IProviderErrorMapper",
]
