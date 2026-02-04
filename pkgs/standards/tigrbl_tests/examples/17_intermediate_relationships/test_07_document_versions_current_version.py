"""Example: document-to-version history with a one-to-one current version."""

from __future__ import annotations

import inspect

import httpx
import pytest

from examples._support import pick_unique_port, start_uvicorn, stop_uvicorn
from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.types import App, Column, ForeignKey, Integer, String, relationship


@pytest.mark.asyncio
async def test_document_versions_current_version() -> None:
    """Link a document to its current version while keeping a history."""

    # Step 1: Define the document with a current_version foreign key.
    class Document(Base):
        __tablename__ = "lesson_doc_current_document"
        __resource__ = "document"
        __allow_unmapped__ = True

        id = Column(Integer, primary_key=True)
        title = Column(String, nullable=False)
        body = Column(String, nullable=False)
        current_version_id = Column(
            Integer,
            ForeignKey("lesson_doc_current_version.id"),
            nullable=True,
        )
        current_version = relationship(
            "DocumentVersion",
            foreign_keys=[current_version_id],
            uselist=False,
        )
        version_history = relationship(
            "DocumentVersion",
            back_populates="document",
            foreign_keys="DocumentVersion.document_id",
            cascade="all, delete-orphan",
        )

    # Step 2: Define the version model that belongs to the document.
    class DocumentVersion(Base):
        __tablename__ = "lesson_doc_current_version"
        __resource__ = "document_version"
        __allow_unmapped__ = True

        id = Column(Integer, primary_key=True)
        document_id = Column(
            Integer,
            ForeignKey("lesson_doc_current_document.id"),
            nullable=False,
        )
        version_label = Column(String, nullable=False)
        body_snapshot = Column(String, nullable=False)
        document = relationship(
            "Document",
            back_populates="version_history",
            foreign_keys=[document_id],
        )

    # Step 3: Initialize the API with an in-memory engine.
    api = TigrblApp(engine=mem(async_=False))
    api.include_models([Document, DocumentVersion])
    init_result = api.initialize()
    if inspect.isawaitable(init_result):
        await init_result

    # Step 4: Mount the API routes on the ASGI app.
    app = App()
    app.include_router(api.router)
    api.attach_diagnostics(prefix="", app=app)

    # Step 5: Start uvicorn and exercise the workflow.
    port = pick_unique_port()
    base_url, server, task = await start_uvicorn(app, port=port)
    try:
        async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
            # Create the document that will own the versions.
            create_document = await client.post(
                "/document",
                json={"title": "Guide", "body": "v1 body"},
            )
            assert create_document.status_code == 201
            document_id = create_document.json()["id"]

            # Create the first version snapshot.
            create_version = await client.post(
                "/document_version",
                json={
                    "document_id": document_id,
                    "version_label": "v1",
                    "body_snapshot": "v1 body",
                },
            )
            version_id = create_version.json()["id"]

            # Update the document to point at the current version.
            await client.patch(
                f"/document/{document_id}",
                json={"current_version_id": version_id},
            )

            # Edit the document body and capture a new version.
            await client.patch(
                f"/document/{document_id}",
                json={"body": "v2 body"},
            )
            create_version_two = await client.post(
                "/document_version",
                json={
                    "document_id": document_id,
                    "version_label": "v2",
                    "body_snapshot": "v2 body",
                },
            )
            version_two_id = create_version_two.json()["id"]

            # Move the current_version pointer to the new snapshot.
            update_current = await client.patch(
                f"/document/{document_id}",
                json={"current_version_id": version_two_id},
            )
            assert update_current.status_code == 200
            assert update_current.json()["current_version_id"] == version_two_id
    finally:
        # Tear down the server to keep the test environment clean.
        await stop_uvicorn(server, task)
