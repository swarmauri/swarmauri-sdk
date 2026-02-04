"""Example: one-to-many relationships exposed through Tigrbl REST endpoints."""

from __future__ import annotations

import inspect

import httpx
import pytest

from examples._support import pick_unique_port, start_uvicorn, stop_uvicorn
from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.types import App, Column, ForeignKey, Integer, String, relationship


@pytest.mark.asyncio
async def test_one_to_many_relationship_via_rest() -> None:
    """Show a one-to-many relationship using REST endpoints."""

    # Step 1: Define the parent model for the relationship.
    class Author(Base):
        __tablename__ = "lesson_rel_author"
        __allow_unmapped__ = True

        # Primary key and fields are standard SQLAlchemy columns.
        id = Column(Integer, primary_key=True)
        name = Column(String, nullable=False)
        # The relationship points to the "many" side of the association.
        books = relationship(
            "Book", back_populates="author", cascade="all, delete-orphan"
        )

    # Step 2: Define the child model that carries the foreign key.
    class Book(Base):
        __tablename__ = "lesson_rel_book"
        __allow_unmapped__ = True

        # Each book belongs to exactly one author.
        id = Column(Integer, primary_key=True)
        title = Column(String, nullable=False)
        author_id = Column(Integer, ForeignKey("lesson_rel_author.id"), nullable=False)
        author = relationship("Author", back_populates="books")

    # Step 3: Build the API with an in-memory engine for fast feedback.
    api = TigrblApp(engine=mem(async_=False))
    # Register both models so their REST routes are generated.
    api.include_models([Author, Book])
    init_result = api.initialize()
    if inspect.isawaitable(init_result):
        await init_result

    # Step 4: Mount the API routes on a FastAPI-compatible app.
    app = App()
    app.include_router(api.router)
    api.attach_diagnostics(prefix="", app=app)

    # Step 5: Launch uvicorn and exercise the REST endpoints.
    port = pick_unique_port()
    base_url, server, task = await start_uvicorn(app, port=port)
    try:
        async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
            # Create the parent record first.
            create_author = await client.post("/author", json={"name": "Ada"})
            assert create_author.status_code == 201
            author_id = create_author.json()["id"]

            # Create two books that point at the same author.
            await client.post(
                "/book",
                json={"title": "Computing 101", "author_id": author_id},
            )
            await client.post(
                "/book",
                json={"title": "Advanced Machines", "author_id": author_id},
            )

            # Confirm the list endpoint returns both related records.
            listing = await client.get("/book")
            assert listing.status_code == 200
            books = [item for item in listing.json() if item["author_id"] == author_id]
            assert len(books) == 2
    finally:
        # Always stop uvicorn to avoid leaking tasks.
        await stop_uvicorn(server, task)
