"""Lesson 21.5: App + API security deps and OpenAPI precedence.

This example demonstrates how ``TigrblApp`` and ``TigrblRouter`` security deps
combine when the API is mounted on the app, including shared scheme names that
show OpenAPI precedence behavior.
"""

import inspect

import httpx
import pytest
from tigrbl.security import HTTPBearer

from examples._support import pick_unique_port, start_uvicorn, stop_uvicorn
from tigrbl import Base, TigrblRouter, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, Security, String


@pytest.mark.asyncio
async def test_openapi_security_from_app_and_api_deps() -> None:
    """Confirm shared security schemes merge when app and API deps combine.

    This test configures two security deps on the API, two on the app, and
    reuses one scheme name to demonstrate how OpenAPI merges shared keys.
    """

    # Configuration: define bearer schemes with one shared scheme name.
    shared_app_scheme = HTTPBearer(scheme_name="SharedToken")
    shared_api_scheme = HTTPBearer(scheme_name="SharedToken")
    app_only_scheme = HTTPBearer(scheme_name="AppOnly")
    api_only_scheme = HTTPBearer(scheme_name="ApiOnly")

    # Configuration: declare a model to mount on the API.
    class CombinedSecdepsWidget(Base, GUIDPk):
        __tablename__ = "lesson_security_app_api_secdeps_widget"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    # Instantiation: define the API with two security deps (shared + router-only).
    class SecuredApi(TigrblRouter):
        SECURITY_DEPS = (
            Security(shared_api_scheme),
            Security(api_only_scheme),
        )

    router = SecuredApi(engine=mem(async_=False))
    router.include_model(CombinedSecdepsWidget)

    # Instantiation: build the app with two security deps (shared + app-only).
    app = TigrblApp(
        engine=mem(async_=False),
        dependencies=[
            Security(shared_app_scheme),
            Security(app_only_scheme),
        ],
    )
    app.include_router(router)

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
        resource_path = f"/{CombinedSecdepsWidget.__name__.lower()}"

        # Assertion: security schemes include shared + app-only + router-only keys.
        assert response.status_code == 200
        security_items = schema["paths"][resource_path]["get"]["security"]
        security_keys = {key for item in security_items for key in item}
        assert security_keys == {"SharedToken", "AppOnly", "ApiOnly"}
        assert "SharedToken" in schema["components"]["securitySchemes"]

    await stop_uvicorn(server, task)
