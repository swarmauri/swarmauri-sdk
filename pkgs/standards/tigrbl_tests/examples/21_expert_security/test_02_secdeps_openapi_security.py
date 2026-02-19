"""Lesson 21.2: Op-level security dependencies surface in OpenAPI.

This example shows how to add security dependencies directly to specific
operations on a ``TigrblRouter``, mount that API on ``TigrblApp``, and confirm that
only the secured routes advertise security requirements in the OpenAPI schema.
"""

import inspect

import httpx
import pytest
from tigrbl.security import HTTPBearer

from examples._support import pick_unique_port, start_uvicorn, stop_uvicorn
from tigrbl import Base, TigrblRouter, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


@pytest.mark.asyncio
async def test_openapi_security_from_op_secdeps_on_mounted_api() -> None:
    """Confirm op-level sec deps annotate only intended routes in OpenAPI.

    This test adds a bearer-token dependency to the list operation on a
    ``TigrblRouter``, mounts the API on ``TigrblApp``, and verifies that the OpenAPI
    schema flags the list route while leaving create unprotected.
    """

    # Configuration: create a reusable bearer-token dependency instance.
    bearer_scheme = HTTPBearer()

    # Configuration: define a model with a list operation secured via sec deps.
    class SecDepsWidget(Base, GUIDPk):
        __tablename__ = "lesson_security_secdeps_widget"
        __allow_unmapped__ = True
        __tigrbl_ops__ = {
            "list": {
                "alias": "list",
                "target": "list",
                "secdeps": (bearer_scheme,),
            }
        }

        name = Column(String, nullable=False)

    # Instantiation: build the API, include the model, and mount on the app.
    api = TigrblRouter(engine=mem(async_=False))
    api.include_model(SecDepsWidget)

    app = TigrblApp(engine=mem(async_=False))
    app.include_router(api)

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
        resource_path = f"/{SecDepsWidget.__name__.lower()}"

        # Assertion: list is secured, create remains open, schema lists schemes.
        assert response.status_code == 200
        assert "security" in schema["paths"][resource_path]["get"]
        assert "security" not in schema["paths"][resource_path]["post"]
        assert schema["components"]["securitySchemes"]

    await stop_uvicorn(server, task)
