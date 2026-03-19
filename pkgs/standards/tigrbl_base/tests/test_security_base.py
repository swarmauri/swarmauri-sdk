import pytest

from tigrbl_base._base._security_base import (
    OpenAPISecurityDependency,
    validate_openapi_security_scheme,
)


def test_openapi_security_dependency_methods() -> None:
    dep = OpenAPISecurityDependency(
        scheme_name="bearerAuth",
        scheme={"type": "http", "scheme": "bearer"},
        scopes=["read"],
    )

    assert dep.openapi_security_scheme() == {"type": "http", "scheme": "bearer"}
    assert dep.openapi_security_requirement() == {"bearerAuth": ["read"]}
    assert dep(request=object()) is None


@pytest.mark.parametrize(
    ("scheme", "message"),
    [
        ({"type": "bad"}, "type' must be one"),
        ({"type": "apiKey", "scheme": "x"}, "'scheme' is only valid"),
        ({"type": "http"}, "requires a non-empty 'scheme'"),
        ({"type": "apiKey", "in": "bad", "name": "n"}, "requires 'in'"),
        ({"type": "apiKey", "in": "header"}, "requires 'name'"),
        ({"type": "oauth2"}, "requires a 'flows'"),
        ({"type": "openIdConnect"}, "requires 'openIdConnectUrl'"),
    ],
)
def test_validate_openapi_security_scheme_errors(scheme: dict, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        validate_openapi_security_scheme(scheme)
