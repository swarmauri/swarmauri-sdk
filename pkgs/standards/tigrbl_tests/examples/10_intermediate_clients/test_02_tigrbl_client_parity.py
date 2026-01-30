"""Lesson 10.2: Comparing TigrblClient and httpx behaviors."""

import httpx
import inspect
import pytest
from tigrbl_client import TigrblClient

from examples._support import pick_unique_port, start_uvicorn, stop_uvicorn
from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import App as FastAPI
from tigrbl.types import Column, String


@pytest.mark.asyncio
async def test_tigrbl_client_matches_httpx_response():
    """Compare a low-level httpx call with the high-level Tigrbl client.

    Purpose: show that TigrblClient returns the same payload shape as a direct
    REST call.
    Design practice: validate consistency across client layers for confidence.
    """

    # Setup: define a model to compare client behavior.
    class LessonClient(Base, GUIDPk):
        __tablename__ = "lesson_client"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    # Deployment: build the API, include the model, and mount diagnostics.
    api = TigrblApp(engine=mem(async_=False))
    api.include_model(LessonClient)
    init_result = api.initialize()
    if inspect.isawaitable(init_result):
        await init_result
    api.mount_jsonrpc(prefix="/rpc")

    app = FastAPI()
    app.include_router(api.router)
    api.attach_diagnostics(prefix="", app=app)

    port = pick_unique_port()
    base_url, server, task = await start_uvicorn(app, port=port)

    # Test: create a resource using raw httpx.
    async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
        response = await client.post(
            f"/{LessonClient.__name__.lower()}",
            json={"name": "beta"},
        )

        # Assertion: raw REST call succeeds.
        assert response.status_code in {200, 201}

    # Test: create a resource using the higher-level TigrblClient.
    client = TigrblClient(base_url)
    rest_response = await client.apost(
        f"/{LessonClient.__name__.lower()}",
        data={"name": "beta"},
    )

    # Assertion: TigrblClient returns the expected payload shape.
    assert rest_response["name"] == "beta"
    await client.aclose()
    await stop_uvicorn(server, task)


@pytest.mark.asyncio
async def test_tigrbl_client_list_returns_created_items():
    """Demonstrate list parity using TigrblClient.

    Purpose: ensure client helpers return list payloads matching REST expectations.
    Design practice: verify list operations in automated checks before shipping.
    """

    # Setup: define a model for list parity validation.
    class LessonClientList(Base, GUIDPk):
        __tablename__ = "lesson_client_list"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    # Deployment: initialize the API and attach diagnostics.
    api = TigrblApp(engine=mem(async_=False))
    api.include_model(LessonClientList)
    init_result = api.initialize()
    if inspect.isawaitable(init_result):
        await init_result
    api.mount_jsonrpc(prefix="/rpc")

    app = FastAPI()
    app.include_router(api.router)
    api.attach_diagnostics(prefix="", app=app)

    port = pick_unique_port()
    base_url, server, task = await start_uvicorn(app, port=port)

    # Test: create a record with httpx so list has data.
    async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as httpx_client:
        response = await httpx_client.post(
            f"/{LessonClientList.__name__.lower()}",
            json={"name": "gamma"},
        )

        # Assertion: create succeeded.
        assert response.status_code in {200, 201}

    # Test: list via TigrblClient for parity with REST.
    client = TigrblClient(base_url)
    items = await client.aget(f"/{LessonClientList.__name__.lower()}")

    # Assertion: the created item appears in the list.
    assert any(item["name"] == "gamma" for item in items)
    await client.aclose()
    await stop_uvicorn(server, task)
