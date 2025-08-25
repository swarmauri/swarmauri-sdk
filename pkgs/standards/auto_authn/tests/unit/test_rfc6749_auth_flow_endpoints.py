"""Tests for presence of core OAuth2 endpoints and missing authorization endpoint per RFC 6749."""

import pytest
from fastapi import FastAPI

from auto_authn.v2.routers.auth_flows import router


def _collect_paths(app: FastAPI) -> set[str]:
    """Return the set of route paths registered on ``app``."""
    return {route.path for route in app.routes}


@pytest.mark.unit
def test_rfc6749_core_endpoints_present() -> None:
    """Verify implemented credential endpoints exist."""
    app = FastAPI()
    app.include_router(router)
    paths = _collect_paths(app)
    assert {
        "/register",
        "/login",
        "/token",
        "/logout",
        "/token/refresh",
        "/introspect",
    } <= paths


@pytest.mark.unit
def test_rfc6749_authorization_endpoint_present() -> None:
    """The `/authorize` endpoint is now implemented."""
    app = FastAPI()
    app.include_router(router)
    paths = _collect_paths(app)
    assert "/authorize" in paths
