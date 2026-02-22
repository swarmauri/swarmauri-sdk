"""Lesson 21.3: App-level security deps via construction params.

This example demonstrates how to pass security dependencies at ``TigrblApp``
construction time and confirm the OpenAPI schema reflects those requirements
for every route.
"""

from tigrbl.security import Security

import inspect

import httpx
import pytest
from tigrbl.security import HTTPBearer

from examples._support import pick_unique_port, start_uvicorn, stop_uvicorn
from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


@pytest.mark.asyncio
async def test_openapi_security_from_app_constructor_deps() -> None:
    """Show app-level constructor deps become OpenAPI security metadata.

    This test passes security deps into ``TigrblApp`` at construction time and
    verifies that the OpenAPI schema marks both list and create routes.
    """

    # Configuration: define a bearer-token scheme for app-wide security.
    bearer_scheme = HTTPBearer(scheme_name="AppToken")
    app_security_dep = Security(bearer_scheme)

    # Configuration: declare a model for app routing.
    class AppSecdepsWidget(Base, GUIDPk):
        __tablename__ = "lesson_security_app_secdeps_widget"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    # Instantiation: create the app with constructor-level security deps.
    app = TigrblApp(engine=mem(async_=False), dependencies=[app_security_dep])
    app.include_model(AppSecdepsWidget)

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
        resource_path = f"/{AppSecdepsWidget.__name__.lower()}"

        # Assertion: both list and create routes are secured at the app level.
        assert response.status_code == 200
        assert "security" in schema["paths"][resource_path]["get"]
        assert "security" in schema["paths"][resource_path]["post"]
        assert "AppToken" in schema["components"]["securitySchemes"]

    await stop_uvicorn(server, task)
