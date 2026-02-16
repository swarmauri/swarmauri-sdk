"""Lesson 21.4: API-level security deps via construction params.

This example shows how to supply security dependencies for a ``TigrblApi``
through its class configuration and verify that the OpenAPI schema marks
routes as secured when the API runs under Uvicorn.
"""

import inspect

import httpx
import pytest
from tigrbl.security import HTTPBearer
from tigrbl.responses import JSONResponse

from examples._support import pick_unique_port, start_uvicorn, stop_uvicorn
from tigrbl import Base, TigrblApi
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, Security, String


@pytest.mark.asyncio
async def test_openapi_security_from_api_constructor_deps() -> None:
    """Confirm API-level constructor deps appear in OpenAPI security metadata.

    This test defines a ``TigrblApi`` subclass with security deps and verifies
    that the OpenAPI schema marks both list and create routes as secured.
    """

    # Configuration: define a bearer-token scheme for API-wide security.
    bearer_scheme = HTTPBearer(scheme_name="ApiToken")

    # Configuration: declare a model for API routing.
    class ApiSecdepsWidget(Base, GUIDPk):
        __tablename__ = "lesson_security_api_secdeps_widget"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    # Instantiation: define the API class with constructor-level security deps.
    class SecuredApi(TigrblApi):
        SECURITY_DEPS = (Security(bearer_scheme),)

    api = SecuredApi(engine=mem(async_=False))
    api.include_model(ApiSecdepsWidget)

    # Deployment: initialize storage and attach OpenAPI to the API router.
    init_result = api.initialize()
    if inspect.isawaitable(init_result):
        await init_result

    def openapi_endpoint(_request) -> JSONResponse:
        return JSONResponse(api.openapi())

    api.add_route("/openapi.json", openapi_endpoint, methods=["GET"])

    port = pick_unique_port()
    base_url, server, task = await start_uvicorn(api, port=port)

    # Usage: request the OpenAPI schema from the running API.
    async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
        response = await client.get("/openapi.json")
        schema = response.json()
        resource_path = f"/{ApiSecdepsWidget.__name__.lower()}"

        # Assertion: API routes are secured and scheme is registered.
        assert response.status_code == 200
        assert "security" in schema["paths"][resource_path]["get"]
        assert "security" in schema["paths"][resource_path]["post"]
        assert "ApiToken" in schema["components"]["securitySchemes"]

    await stop_uvicorn(server, task)
