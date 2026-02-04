"""Example: document-to-version history using a backref relationship."""

from __future__ import annotations

import inspect

import httpx
import pytest

from examples._support import pick_unique_port, start_uvicorn, stop_uvicorn
from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.types import App, Column, ForeignKey, Integer, String, relationship


@pytest.mark.asyncio
async def test_document_versions_backref() -> None:
    """Create a document and versions using a backref for the reverse link."""

    # Step 1: Define the document model with a backref for versions.
    class Document(Base):
        __tablename__ = "lesson_doc_br_document"
        __resource__ = "document"
        __allow_unmapped__ = True

        id = Column(Integer, primary_key=True)
        title = Column(String, nullable=False)
        body = Column(String, nullable=False)
        version_history = relationship(
            "DocumentVersion",
            backref="document",
            cascade="all, delete-orphan",
        )

    # Step 2: Define the version model with a foreign key only.
    class DocumentVersion(Base):
        __tablename__ = "lesson_doc_br_version"
        __resource__ = "document_version"
        __allow_unmapped__ = True

        id = Column(Integer, primary_key=True)
        document_id = Column(
            Integer,
            ForeignKey("lesson_doc_br_document.id"),
            nullable=False,
        )
        version_label = Column(String, nullable=False)
        body_snapshot = Column(String, nullable=False)

    # Step 3: Initialize the API using an in-memory database.
    api = TigrblApp(engine=mem(async_=False))
    api.include_models([Document, DocumentVersion])
    init_result = api.initialize()
    if inspect.isawaitable(init_result):
        await init_result

    # Step 4: Mount the routes on a FastAPI-compatible app.
    app = App()
    app.include_router(api.router)
    api.attach_diagnostics(prefix="", app=app)

    # Step 5: Launch uvicorn and exercise the REST endpoints.
    port = pick_unique_port()
    base_url, server, task = await start_uvicorn(app, port=port)
    try:
        async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
            # Create a document that will anchor the version history.
            create_document = await client.post(
                "/document",
                json={"title": "Spec", "body": "Original copy"},
            )
            assert create_document.status_code == 201
            document_id = create_document.json()["id"]

            # Record the first version.
            await client.post(
                "/document_version",
                json={
                    "document_id": document_id,
                    "version_label": "v1",
                    "body_snapshot": "Original copy",
                },
            )

            # Update the document body to simulate changes.
            await client.patch(
                f"/document/{document_id}",
                json={"body": "Edited copy"},
            )

            # Record the second version after the update.
            await client.post(
                "/document_version",
                json={
                    "document_id": document_id,
                    "version_label": "v2",
                    "body_snapshot": "Edited copy",
                },
            )

            # Confirm the document has two related versions.
            versions = await client.get("/document_version")
            related = [
                item for item in versions.json() if item["document_id"] == document_id
            ]
            assert len(related) == 2
    finally:
        # Shut down the server so the test cleans up properly.
        await stop_uvicorn(server, task)
