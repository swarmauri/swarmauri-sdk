"""OpenAPI security schemes."""

from ._base import OpenAPISecurityDependency, validate_openapi_security_scheme
from .api_key import APIKey
from .http_bearer import HTTPAuthorizationCredentials, HTTPBearer
from .mutual_tls import MutualTLS
from .oauth2 import OAuth2
from .openid_connect import OpenIdConnect

__all__ = [
    "OpenAPISecurityDependency",
    "validate_openapi_security_scheme",
    "HTTPAuthorizationCredentials",
    "HTTPBearer",
    "APIKey",
    "OAuth2",
    "OpenIdConnect",
    "MutualTLS",
]
