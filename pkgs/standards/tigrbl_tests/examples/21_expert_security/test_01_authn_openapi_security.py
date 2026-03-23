"""Lesson 21.1: Authn dependencies update OpenAPI security per route.

This example demonstrates how to configure authn dependencies on both
``TigrblApp`` and ``TigrblRouter``, allow anonymous access to selected operations,
and confirm OpenAPI reflects security requirements on a per-route basis.
"""

import inspect

import httpx
import pytest
from tigrbl import TableBase, TigrblApp, TigrblRouter
from tigrbl.shortcuts.engine import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl import JSONResponse
from tigrbl import HTTPBearer
from tigrbl._concrete._security.http_bearer import HTTPAuthorizationCredentials
from tigrbl.security import Security
from tigrbl.types import Column, String
from tigrbl_tests.examples._support import pick_unique_port, start_uvicorn, stop_uvicorn


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
    class SecureWidget(TableBase, GUIDPk):
        __tablename__ = "lesson_security_authn_widget"
        __allow_unmapped__ = True
        __tigrbl_allow_anon__ = ("list",)

        name = Column(String, nullable=False)

    # Instantiation: build the app, apply authn, and include the model.
    app = TigrblApp(engine=mem(async_=False))
    app.set_auth(authn=authn_dependency)
    app.include_table(SecureWidget)

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
async def test_openapi_security_from_router_authn_dependency() -> None:
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
    class SecureApiWidget(TableBase, GUIDPk):
        __tablename__ = "lesson_security_authn_router_widget"
        __allow_unmapped__ = True
        __tigrbl_allow_anon__ = ("list",)

        name = Column(String, nullable=False)

    # Instantiation: build the API, apply authn, and include the model.
    router = TigrblRouter(engine=mem(async_=False))
    router.set_auth(authn=authn_dependency)
    router.include_table(SecureApiWidget)

    # Deployment: initialize storage, attach OpenAPI, mount router, and run with Uvicorn.
    init_result = router.initialize()
    if inspect.isawaitable(init_result):
        await init_result

    # Deployment: mount the router in an app and expose OpenAPI on the host app.
    app = TigrblApp(engine=mem(async_=False))
    app.include_router(router)

    def openapi_endpoint(_request) -> JSONResponse:
        return JSONResponse(app.openapi())

    openapi_router = TigrblRouter()
    openapi_router.add_route("/openapi.json", openapi_endpoint, methods=["GET"])
    app.include_router(openapi_router)

    port = pick_unique_port()
    base_url, server, task = await start_uvicorn(app, port=port)

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


def test_app_set_auth_updates_auth_configuration() -> None:
    """Show ``app.set_auth(...)`` updates auth-related app configuration."""

    bearer_scheme = HTTPBearer()
    optional_bearer_scheme = HTTPBearer(auto_error=False)

    async def authn_dependency(
        credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    ) -> dict[str, str]:
        return {"sub": credentials.credentials}

    async def optional_authn_dependency(
        credentials: HTTPAuthorizationCredentials | None = Security(
            optional_bearer_scheme
        ),
    ) -> dict[str, str] | None:
        if credentials is None:
            return None
        return {"sub": credentials.credentials}

    def authorize_dependency() -> None: ...

    app = TigrblApp(engine=mem(async_=False))
    app.set_auth(
        authn=authn_dependency,
        authorize=authorize_dependency,
        optional_authn_dep=optional_authn_dependency,
    )

    assert app._authn is authn_dependency
    assert app._allow_anon is False
    assert app._authorize is authorize_dependency
    assert app._optional_authn_dep is optional_authn_dependency


def test_app_set_auth_refreshes_security_for_preincluded_tables() -> None:
    """Show ``app.set_auth(...)`` updates route security after table inclusion."""

    class SecurityRefreshWidget(TableBase, GUIDPk):
        __tablename__ = "lesson_security_refresh_widget"
        __allow_unmapped__ = True
        __tigrbl_allow_anon__ = ("list",)

        name = Column(String, nullable=False)

    app = TigrblApp(engine=mem(async_=False))
    app.include_table(SecurityRefreshWidget)
    app.set_auth(authn=lambda cred=Security(HTTPBearer()): cred, allow_anon=False)

    ops_by_alias = getattr(SecurityRefreshWidget.ops, "by_alias", {})
    assert tuple(ops_by_alias["list"])[0].secdeps == ()
    assert tuple(ops_by_alias["create"])[0].secdeps == (app._authn,)
