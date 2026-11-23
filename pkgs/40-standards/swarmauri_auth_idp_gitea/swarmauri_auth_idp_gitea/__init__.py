"""Gitea identity provider implementations for Swarmauri."""

from .GiteaOAuth20AppClient import GiteaOAuth20AppClient
from .GiteaOAuth20Login import GiteaOAuth20Login
from .GiteaOAuth21AppClient import GiteaOAuth21AppClient
from .GiteaOAuth21Login import GiteaOAuth21Login
from .GiteaOIDC10AppClient import GiteaOIDC10AppClient
from .GiteaOIDC10Login import GiteaOIDC10Login

__all__ = [
    "GiteaOAuth20AppClient",
    "GiteaOAuth20Login",
    "GiteaOAuth21AppClient",
    "GiteaOAuth21Login",
    "GiteaOIDC10AppClient",
    "GiteaOIDC10Login",
]
