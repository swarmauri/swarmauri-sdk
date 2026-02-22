"""Lesson 21.1: Authn dependencies update OpenAPI security per route.

This example demonstrates how to configure authn dependencies on both
``TigrblApp`` and ``TigrblRouter``, allow anonymous access to selected operations,
and confirm OpenAPI reflects security requirements on a per-route basis.
"""

from tigrbl.security import Security

import inspect

import httpx
import pytest
from tigrbl.responses import JSONResponse
from tigrbl.security import HTTPAuthorizationCredentials, HTTPBearer

from examples._support import pick_unique_port, start_uvicorn, stop_uvicorn
from tigrbl import Base, TigrblRouter, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


@pytest.mark.asyncio
async def test_openapi_security_from_app_authn_dependency() -> None:
    """Show app-level authn dependencies mark secured routes in OpenAPI.

    This test configures a bearer-token authn dependency on ``TigrblApp``,
    allows anonymous access to list operations, and asserts that only the
    secured routes include OpenAPI security metadata.
    """

    # Configuration: define a bearer-token scheme and an authn dependency.
    bearer_scheme = HTTPBearer()

    async def authn_dependency(
        credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    ) -> dict[str, str]:
        return {"sub": credentials.credentials}

    # Configuration: declare a model with anonymous list access.
    class SecureWidget(Base, GUIDPk):
        __tablename__ = "lesson_security_authn_widget"
        __allow_unmapped__ = True
        __tigrbl_allow_anon__ = ("list",)

        name = Column(String, nullable=False)

    # Instantiation: build the app, apply authn, and include the model.
    app = TigrblApp(engine=mem(async_=False))
    app.set_auth(authn=authn_dependency)
    app.include_model(SecureWidget)

    # Deployment: initialize storage and run the app with Uvicorn.
    init_result = app.initialize()
    if inspect.isawaitable(init_result):
        await init_result

    port = pick_unique_port()
    base_url, server, task = await start_uvicorn(app, port=port)

    # Usage: request the OpenAPI schema from the running app.
    async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
        response = await client.get("/openapi.json")
        schema = response.json()
        resource_path = f"/{SecureWidget.__name__.lower()}"

        # Assertion: secured routes include security metadata; anon routes do not.
        assert response.status_code == 200
        assert "security" in schema["paths"][resource_path]["post"]
        assert "security" not in schema["paths"][resource_path]["get"]
        assert schema["components"]["securitySchemes"]

    await stop_uvicorn(server, task)


@pytest.mark.asyncio
async def test_openapi_security_from_api_authn_dependency() -> None:
    """Show API-level authn dependencies mark secured routes in OpenAPI.

    This test configures a bearer-token authn dependency on ``TigrblRouter``,
    allows anonymous access to list operations, and asserts that only the
    secured routes include OpenAPI security metadata.
    """

    # Configuration: define a bearer-token scheme and an authn dependency.
    bearer_scheme = HTTPBearer()

    async def authn_dependency(
        credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    ) -> dict[str, str]:
        return {"sub": credentials.credentials}

    # Configuration: declare a model with anonymous list access.
    class SecureApiWidget(Base, GUIDPk):
        __tablename__ = "lesson_security_authn_api_widget"
        __allow_unmapped__ = True
        __tigrbl_allow_anon__ = ("list",)

        name = Column(String, nullable=False)

    # Instantiation: build the API, apply authn, and include the model.
    api = TigrblRouter(engine=mem(async_=False))
    api.set_auth(authn=authn_dependency)
    api.include_model(SecureApiWidget)

    # Deployment: initialize storage, attach OpenAPI, and run with Uvicorn.
    init_result = api.initialize()
    if inspect.isawaitable(init_result):
        await init_result

    # Deployment: add an OpenAPI endpoint directly on the router-only API.
    def openapi_endpoint(_request) -> JSONResponse:
        return JSONResponse(api.openapi())

    api.add_route("/openapi.json", openapi_endpoint, methods=["GET"])

    port = pick_unique_port()
    base_url, server, task = await start_uvicorn(api, port=port)

    # Usage: request the OpenAPI schema from the running API.
    async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
        response = await client.get("/openapi.json")
        schema = response.json()
        resource_path = f"/{SecureApiWidget.__name__.lower()}"

        # Assertion: secured routes include security metadata; anon routes do not.
        assert response.status_code == 200
        assert "security" in schema["paths"][resource_path]["post"]
        assert "security" not in schema["paths"][resource_path]["get"]
        assert schema["components"]["securitySchemes"]

    await stop_uvicorn(server, task)
