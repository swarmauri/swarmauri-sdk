"""Example: self-referential relationships exposed through REST endpoints."""

from __future__ import annotations

import inspect

import httpx
import pytest

from examples._support import pick_unique_port, start_uvicorn, stop_uvicorn
from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.types import App, Column, ForeignKey, Integer, String, relationship


@pytest.mark.asyncio
async def test_self_referential_relationship_via_rest() -> None:
    """Show a self-referential relationship for hierarchical data."""

    # Step 1: Define a hierarchical model that references itself.
    class Category(Base):
        __tablename__ = "lesson_rel_category"
        __allow_unmapped__ = True

        # Each category can optionally point at a parent category.
        id = Column(Integer, primary_key=True)
        name = Column(String, nullable=False)
        parent_id = Column(Integer, ForeignKey("lesson_rel_category.id"))
        parent = relationship("Category", remote_side=[id], back_populates="children")
        children = relationship(
            "Category", back_populates="parent", cascade="all, delete-orphan"
        )

    # Step 2: Build the API with a memory engine for speed.
    api = TigrblApp(engine=mem(async_=False))
    api.include_model(Category)
    init_result = api.initialize()
    if inspect.isawaitable(init_result):
        await init_result

    # Step 3: Mount the API routes on an application instance.
    app = App()
    app.include_router(api.router)
    api.attach_diagnostics(prefix="", app=app)

    # Step 4: Start uvicorn and exercise the endpoints.
    port = pick_unique_port()
    base_url, server, task = await start_uvicorn(app, port=port)
    try:
        async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
            # Create the root category first.
            create_root = await client.post("/category", json={"name": "Root"})
            assert create_root.status_code == 201
            root_id = create_root.json()["id"]

            # Create a child that references the root.
            create_child = await client.post(
                "/category",
                json={"name": "Child", "parent_id": root_id},
            )
            assert create_child.status_code == 201
            child_id = create_child.json()["id"]

            # Read the child to confirm the parent_id value.
            read_child = await client.get(f"/category/{child_id}")
            assert read_child.status_code == 200
            assert read_child.json()["parent_id"] == root_id
    finally:
        # Ensure the server is stopped even if assertions fail.
        await stop_uvicorn(server, task)
