"""Azure Active Directory identity provider implementations."""

from .AzureOAuth20Login import AzureOAuth20Login
from .AzureOAuth21Login import AzureOAuth21Login
from .AzureOIDC10Login import AzureOIDC10Login

__all__ = [
    "AzureOAuth20Login",
    "AzureOAuth21Login",
    "AzureOIDC10Login",
]
