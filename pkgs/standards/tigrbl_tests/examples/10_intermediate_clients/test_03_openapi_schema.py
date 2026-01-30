"""Lesson 10.3: Inspecting the OpenAPI schema."""

import httpx
import inspect
import pytest

from examples._support import pick_unique_port, start_uvicorn, stop_uvicorn
from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import App as FastAPI
from tigrbl.types import Column, String


@pytest.mark.asyncio
async def test_openapi_schema_contains_widget_paths():
    """Confirm generated OpenAPI includes model-specific paths.

    Purpose: show that API documentation reflects registered models.
    Design practice: use OpenAPI output to validate route exposure.
    """

    # Setup: define a model to ensure OpenAPI includes its paths.
    class LessonOpenAPI(Base, GUIDPk):
        __tablename__ = "lesson_openapi"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    # Deployment: build an API, include the model, and mount diagnostics.
    api = TigrblApp(engine=mem(async_=False))
    api.include_model(LessonOpenAPI)
    init_result = api.initialize()
    if inspect.isawaitable(init_result):
        await init_result
    api.mount_jsonrpc(prefix="/rpc")

    app = FastAPI()
    app.include_router(api.router)
    api.attach_diagnostics(prefix="", app=app)

    port = pick_unique_port()
    base_url, server, task = await start_uvicorn(app, port=port)

    # Test: fetch the OpenAPI schema via httpx.
    async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
        response = await client.get("/openapi.json")

        # Assertion: OpenAPI returns successfully and includes model paths.
        assert response.status_code == 200
        assert f"/{LessonOpenAPI.__name__.lower()}" in response.json()["paths"]

    await stop_uvicorn(server, task)


@pytest.mark.asyncio
async def test_openapi_schema_includes_get_and_post():
    """Show that OpenAPI documents REST verbs for the model path.

    Purpose: ensure both list and create operations appear for the resource.
    Design practice: check documentation parity whenever defaults are customized.
    """

    # Setup: declare a model to verify REST verbs are documented.
    class LessonOpenAPIPaths(Base, GUIDPk):
        __tablename__ = "lesson_openapi_paths"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    # Deployment: initialize the app and attach diagnostics.
    api = TigrblApp(engine=mem(async_=False))
    api.include_model(LessonOpenAPIPaths)
    init_result = api.initialize()
    if inspect.isawaitable(init_result):
        await init_result
    api.mount_jsonrpc(prefix="/rpc")

    app = FastAPI()
    app.include_router(api.router)
    api.attach_diagnostics(prefix="", app=app)

    port = pick_unique_port()
    base_url, server, task = await start_uvicorn(app, port=port)

    # Test: inspect the OpenAPI paths for the model.
    async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
        response = await client.get("/openapi.json")
        paths = response.json()["paths"]
        methods = paths[f"/{LessonOpenAPIPaths.__name__.lower()}"].keys()

        # Assertion: both list (get) and create (post) are documented.
        assert "get" in methods
        assert "post" in methods

    await stop_uvicorn(server, task)
