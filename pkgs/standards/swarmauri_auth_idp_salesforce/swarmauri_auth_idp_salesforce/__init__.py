"""Salesforce identity provider implementations for Swarmauri."""

from .SalesforceOAuth20Login import SalesforceOAuth20Login
from .SalesforceOAuth21Login import SalesforceOAuth21Login
from .SalesforceOIDC10Login import SalesforceOIDC10Login

__all__ = [
    "SalesforceOAuth20Login",
    "SalesforceOAuth21Login",
    "SalesforceOIDC10Login",
]
