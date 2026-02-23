from types import SimpleNamespace

import pytest

from tigrbl.security import APIKey, HTTPBearer, MutualTLS, OAuth2, OpenIdConnect
from tigrbl.security.schemes import OpenAPISecurityDependency


@pytest.mark.unit
def test_scheme_classes_are_exposed_from_security_modules() -> None:
    assert issubclass(HTTPBearer, OpenAPISecurityDependency)
    assert issubclass(APIKey, OpenAPISecurityDependency)
    assert issubclass(OAuth2, OpenAPISecurityDependency)
    assert issubclass(OpenIdConnect, OpenAPISecurityDependency)
    assert issubclass(MutualTLS, OpenAPISecurityDependency)


@pytest.mark.unit
def test_http_bearer_reads_authorization_header() -> None:
    dep = HTTPBearer()
    request = SimpleNamespace(headers={"authorization": "bearer token-123"})

    credentials = dep(request)

    assert credentials is not None
    assert credentials.scheme == "bearer"
    assert credentials.credentials == "token-123"


@pytest.mark.unit
def test_api_key_reads_value_from_query_params() -> None:
    dep = APIKey(name="api_key", in_="query")
    request = SimpleNamespace(headers={}, query_params={"api_key": "secret-value"})

    assert dep(request) == "secret-value"


@pytest.mark.unit
def test_api_key_missing_value_raises_when_auto_error_enabled() -> None:
    dep = APIKey(name="api_key", in_="header", auto_error=True)
    request = SimpleNamespace(headers={}, query_params={})

    from tigrbl.runtime.status.exceptions import HTTPException

    with pytest.raises(HTTPException):
        dep(request)
