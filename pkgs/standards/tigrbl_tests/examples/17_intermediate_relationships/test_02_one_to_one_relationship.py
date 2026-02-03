"""Example: one-to-one relationships exposed through Tigrbl REST endpoints."""

from __future__ import annotations

import inspect

import httpx
import pytest

from examples._support import pick_unique_port, start_uvicorn, stop_uvicorn
from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.types import App, Column, ForeignKey, Integer, String, relationship


@pytest.mark.asyncio
async def test_one_to_one_relationship_via_rest() -> None:
    """Show a one-to-one relationship using REST endpoints."""

    # Step 1: Define the user with a single profile relationship.
    class User(Base):
        __tablename__ = "lesson_rel_user"
        __allow_unmapped__ = True

        # Each user has a single profile.
        id = Column(Integer, primary_key=True)
        username = Column(String, nullable=False)
        profile = relationship("Profile", back_populates="user", uselist=False)

    # Step 2: Define the profile with a unique foreign key.
    class Profile(Base):
        __tablename__ = "lesson_rel_profile"
        __allow_unmapped__ = True

        # Enforce one-to-one by making user_id unique.
        id = Column(Integer, primary_key=True)
        display_name = Column(String, nullable=False)
        user_id = Column(
            Integer, ForeignKey("lesson_rel_user.id"), nullable=False, unique=True
        )
        user = relationship("User", back_populates="profile")

    # Step 3: Initialize the API with an in-memory engine.
    api = TigrblApp(engine=mem(async_=False))
    # Register the related models so both REST resources are available.
    api.include_models([User, Profile])
    init_result = api.initialize()
    if inspect.isawaitable(init_result):
        await init_result

    # Step 4: Mount Tigrbl routes on the application.
    app = App()
    app.include_router(api.router)
    api.attach_diagnostics(prefix="", app=app)

    # Step 5: Deploy uvicorn and exercise the REST endpoints.
    port = pick_unique_port()
    base_url, server, task = await start_uvicorn(app, port=port)
    try:
        async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
            # Create the user first to satisfy the profile foreign key.
            create_user = await client.post("/user", json={"username": "grace"})
            assert create_user.status_code == 201
            user_id = create_user.json()["id"]

            # Create the profile that references the user.
            create_profile = await client.post(
                "/profile",
                json={"display_name": "Grace Hopper", "user_id": user_id},
            )
            assert create_profile.status_code == 201

            # Read back the profile to verify the link.
            profile_id = create_profile.json()["id"]
            read_profile = await client.get(f"/profile/{profile_id}")
            assert read_profile.status_code == 200
            assert read_profile.json()["user_id"] == user_id
    finally:
        # Ensure the uvicorn server is shut down.
        await stop_uvicorn(server, task)
