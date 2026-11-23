from importlib.metadata import PackageNotFoundError, version

from .OpenRouterAuthConfig import OpenRouterAuthConfig
from .OpenRouterEndpoints import OpenRouterEndpoints
from .OpenRouterErrorMapper import OpenRouterErrorMapper
from .OpenRouterModelCatalog import OpenRouterModelCatalog
from .OpenRouterProvider import OpenRouterProvider
from .OpenRouterProviderPreferences import OpenRouterProviderPreferences
from .OpenRouterToolSchemaConverter import OpenRouterToolSchemaConverter

__all__ = [
    "OpenRouterAuthConfig",
    "OpenRouterEndpoints",
    "OpenRouterErrorMapper",
    "OpenRouterModelCatalog",
    "OpenRouterProvider",
    "OpenRouterProviderPreferences",
    "OpenRouterToolSchemaConverter",
]

try:
    __version__ = version("swarmauri_provider_openrouter")
except PackageNotFoundError:
    __version__ = "0.0.0"
