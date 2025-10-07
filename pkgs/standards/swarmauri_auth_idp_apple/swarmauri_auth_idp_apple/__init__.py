"""Apple identity provider implementations for Swarmauri."""

from .AppleOAuth20AppClient import AppleOAuth20AppClient
from .AppleOAuth20Login import AppleOAuth20Login
from .AppleOAuth21AppClient import AppleOAuth21AppClient
from .AppleOAuth21Login import AppleOAuth21Login
from .AppleOIDC10AppClient import AppleOIDC10AppClient
from .AppleOIDC10Login import AppleOIDC10Login

__all__ = [
    "AppleOAuth20AppClient",
    "AppleOAuth21AppClient",
    "AppleOIDC10AppClient",
    "AppleOAuth20Login",
    "AppleOAuth21Login",
    "AppleOIDC10Login",
]
