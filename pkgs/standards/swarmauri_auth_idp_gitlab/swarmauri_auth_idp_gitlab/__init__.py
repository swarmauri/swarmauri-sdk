"""GitLab identity provider implementations for Swarmauri."""

from .GitLabOAuth20AppClient import GitLabOAuth20AppClient
from .GitLabOAuth20Login import GitLabOAuth20Login
from .GitLabOAuth21AppClient import GitLabOAuth21AppClient
from .GitLabOAuth21Login import GitLabOAuth21Login
from .GitLabOIDC10AppClient import GitLabOIDC10AppClient
from .GitLabOIDC10Login import GitLabOIDC10Login

__all__ = [
    "GitLabOAuth20AppClient",
    "GitLabOAuth20Login",
    "GitLabOAuth21AppClient",
    "GitLabOAuth21Login",
    "GitLabOIDC10AppClient",
    "GitLabOIDC10Login",
]
