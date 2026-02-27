"""Lesson 21.4: Router-level security deps via construction params.

This example shows how to supply security dependencies for a ``TigrblRouter``
through its class configuration and verify that the OpenAPI schema marks
routes as secured when the API runs under Uvicorn.
"""

from tigrbl.security import Security

import inspect

import httpx
import pytest
from tigrbl.security import HTTPBearer
from tigrbl.shortcuts.responses import JSONResponse

from tigrbl_tests.examples._support import pick_unique_port, start_uvicorn, stop_uvicorn
from tigrbl import Base, TigrblApp, TigrblRouter
from tigrbl.shortcuts.engine import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


@pytest.mark.asyncio
async def test_openapi_security_from_router_constructor_deps() -> None:
    """Confirm Router-level constructor deps appear in OpenAPI security metadata.

    This test defines a ``TigrblRouter`` subclass with security deps and verifies
    that the OpenAPI schema marks both list and create routes as secured.
    """

    # Configuration: define a bearer-token scheme for Router-wide security.
    bearer_scheme = HTTPBearer(scheme_name="ApiToken")

    # Configuration: declare a model for API routing.
    class RouterSecdepsWidget(Base, GUIDPk):
        __tablename__ = "lesson_security_router_secdeps_widget"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    # Instantiation: define the API class with constructor-level security deps.
    class SecuredRouter(TigrblRouter):
        SECURITY_DEPS = (Security(bearer_scheme),)

    router = SecuredRouter(engine=mem(async_=False))
    router.include_table(RouterSecdepsWidget)

    # Deployment: initialize storage, attach OpenAPI, mount router, and run with Uvicorn.
    init_result = router.initialize()
    if inspect.isawaitable(init_result):
        await init_result

    def openapi_endpoint(_request) -> JSONResponse:
        return JSONResponse(router.openapi())

    router.add_route("/openapi.json", openapi_endpoint, methods=["GET"])

    app = TigrblApp(engine=mem(async_=False))
    app.include_router(router)

    port = pick_unique_port()
    base_url, server, task = await start_uvicorn(app, port=port)

    # Usage: request the OpenAPI schema from the running API.
    async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
        response = await client.get("/openapi.json")
        schema = response.json()
        resource_path = f"/{RouterSecdepsWidget.__name__.lower()}"

        # Assertion: API routes are secured and scheme is registered.
        assert response.status_code == 200
        assert "security" in schema["paths"][resource_path]["get"]
        assert "security" in schema["paths"][resource_path]["post"]
        assert "ApiToken" in schema["components"]["securitySchemes"]

    await stop_uvicorn(server, task)
