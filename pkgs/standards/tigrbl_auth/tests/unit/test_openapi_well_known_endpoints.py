import asyncio

import pytest_asyncio

from tigrbl_auth.app import app
from tigrbl_auth.routers.surface import surface_api
from tigrbl_auth.rfc8414_metadata import JWKS_PATH


@pytest_asyncio.fixture()
async def openapi_spec() -> dict:
    """Generate an OpenAPI specification after initializing the API surface."""
    init = surface_api.initialize()
    if asyncio.iscoroutine(init):
        await init
    return app.openapi()


def test_openapi_includes_openid_configuration(openapi_spec: dict) -> None:
    """Ensure the discovery document is documented in OpenAPI."""
    assert "/.well-known/openid-configuration" in openapi_spec["paths"]


def test_openapi_includes_jwks(openapi_spec: dict) -> None:
    """Ensure the JWKS endpoint is documented in OpenAPI."""
    assert JWKS_PATH in openapi_spec["paths"]
