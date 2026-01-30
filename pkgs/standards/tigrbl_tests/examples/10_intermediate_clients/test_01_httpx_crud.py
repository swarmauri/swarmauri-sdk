"""Lesson 10.1: Using httpx for REST CRUD workflows."""

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
async def test_httpx_crud_roundtrip():
    """Walk through a minimal REST create call with httpx.

    Purpose: demonstrate a direct HTTP client workflow for creating resources.
    Design practice: always assert status codes and cleanly close clients.
    """

    # Setup: define a model inline for the REST endpoint.
    class LessonHttpx(Base, GUIDPk):
        __tablename__ = "lesson_httpx"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    # Deployment: create the API, include the model, and mount diagnostics.
    api = TigrblApp(engine=mem(async_=False))
    api.include_model(LessonHttpx)
    init_result = api.initialize()
    if inspect.isawaitable(init_result):
        await init_result
    api.mount_jsonrpc(prefix="/rpc")

    app = FastAPI()
    app.include_router(api.router)
    api.attach_diagnostics(prefix="", app=app)

    port = pick_unique_port()
    base_url, server, task = await start_uvicorn(app, port=port)

    # Test: perform a REST create with httpx against the running server.
    async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
        response = await client.post(
            f"/{LessonHttpx.__name__.lower()}",
            json={"name": "alpha"},
        )

        # Assertion: the create endpoint accepts the payload.
        assert response.status_code in {200, 201}

    await stop_uvicorn(server, task)


@pytest.mark.asyncio
async def test_httpx_list_returns_collection():
    """Demonstrate listing resources after a create.

    Purpose: show the list endpoint returns a collection response.
    Design practice: verify response shape alongside status codes.
    """

    # Setup: define a model for list/collection behavior.
    class LessonHttpxList(Base, GUIDPk):
        __tablename__ = "lesson_httpx_list"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    # Deployment: include the model and mount diagnostics on the app.
    api = TigrblApp(engine=mem(async_=False))
    api.include_model(LessonHttpxList)
    init_result = api.initialize()
    if inspect.isawaitable(init_result):
        await init_result
    api.mount_jsonrpc(prefix="/rpc")

    app = FastAPI()
    app.include_router(api.router)
    api.attach_diagnostics(prefix="", app=app)

    port = pick_unique_port()
    base_url, server, task = await start_uvicorn(app, port=port)

    # Test: create then list the collection via httpx.
    async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
        create_response = await client.post(
            f"/{LessonHttpxList.__name__.lower()}",
            json={"name": "alpha"},
        )

        # Assertion: the create request succeeds.
        assert create_response.status_code in {200, 201}

        list_response = await client.get(f"/{LessonHttpxList.__name__.lower()}")

        # Assertion: the list request returns a collection.
        assert list_response.status_code == 200
        assert isinstance(list_response.json(), list)

    await stop_uvicorn(server, task)
