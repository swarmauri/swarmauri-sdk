"""Example: document-to-version history using back_populates relationships."""

from __future__ import annotations

import inspect

import httpx
import pytest

from examples._support import pick_unique_port, start_uvicorn, stop_uvicorn
from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.types import App, Column, ForeignKey, Integer, String, relationship


@pytest.mark.asyncio
async def test_document_versions_back_populates() -> None:
    """Create a document, update it, and add linked versions via REST."""

    # Step 1: Define a document model with a version history relationship.
    class Document(Base):
        __tablename__ = "lesson_doc_bp_document"
        __resource__ = "document"
        __allow_unmapped__ = True

        id = Column(Integer, primary_key=True)
        title = Column(String, nullable=False)
        body = Column(String, nullable=False)
        version_history = relationship(
            "DocumentVersion",
            back_populates="document",
            cascade="all, delete-orphan",
        )

    # Step 2: Define the version model that points back to the document.
    class DocumentVersion(Base):
        __tablename__ = "lesson_doc_bp_version"
        __resource__ = "document_version"
        __allow_unmapped__ = True

        id = Column(Integer, primary_key=True)
        document_id = Column(
            Integer,
            ForeignKey("lesson_doc_bp_document.id"),
            nullable=False,
        )
        version_label = Column(String, nullable=False)
        body_snapshot = Column(String, nullable=False)
        document = relationship("Document", back_populates="version_history")

    # Step 3: Build the API with an in-memory engine for quick feedback.
    api = TigrblApp(engine=mem(async_=False))
    api.include_models([Document, DocumentVersion])
    init_result = api.initialize()
    if inspect.isawaitable(init_result):
        await init_result

    # Step 4: Mount the generated REST routes on the ASGI app.
    app = App()
    app.include_router(api.router)
    api.attach_diagnostics(prefix="", app=app)

    # Step 5: Start uvicorn and exercise the document/version workflow.
    port = pick_unique_port()
    base_url, server, task = await start_uvicorn(app, port=port)
    try:
        async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
            # Create the document first so versions can reference it.
            create_document = await client.post(
                "/document",
                json={"title": "Draft", "body": "Initial text"},
            )
            assert create_document.status_code == 201
            document_id = create_document.json()["id"]

            # Create the first version from the initial content.
            create_version_one = await client.post(
                "/document_version",
                json={
                    "document_id": document_id,
                    "version_label": "v1",
                    "body_snapshot": "Initial text",
                },
            )
            assert create_version_one.status_code == 201

            # Update the document to simulate edits.
            update_document = await client.patch(
                f"/document/{document_id}",
                json={"body": "Revised text"},
            )
            assert update_document.status_code == 200

            # Store a second version capturing the updated content.
            create_version_two = await client.post(
                "/document_version",
                json={
                    "document_id": document_id,
                    "version_label": "v2",
                    "body_snapshot": "Revised text",
                },
            )
            assert create_version_two.status_code == 201

            # Verify both versions are linked to the same document.
            versions = await client.get("/document_version")
            assert versions.status_code == 200
            linked_versions = [
                item for item in versions.json() if item["document_id"] == document_id
            ]
            assert len(linked_versions) == 2
    finally:
        # Always stop uvicorn to avoid leaving background tasks running.
        await stop_uvicorn(server, task)
