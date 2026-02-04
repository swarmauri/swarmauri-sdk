"""Example: ordered document versions with explicit relationship options."""

from __future__ import annotations

import inspect

import httpx
import pytest

from examples._support import pick_unique_port, start_uvicorn, stop_uvicorn
from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.types import App, Column, ForeignKey, Integer, String, relationship


@pytest.mark.asyncio
async def test_document_versions_ordered_history() -> None:
    """Create and verify ordered document versions over REST."""

    # Step 1: Define the document model with an ordered version history.
    class Document(Base):
        __tablename__ = "lesson_doc_ordered_document"
        __resource__ = "document"
        __allow_unmapped__ = True

        id = Column(Integer, primary_key=True)
        title = Column(String, nullable=False)
        body = Column(String, nullable=False)
        version_history = relationship(
            "DocumentVersion",
            back_populates="document",
            order_by="DocumentVersion.version_index",
            lazy="selectin",
        )

    # Step 2: Define the version model with an explicit ordering column.
    class DocumentVersion(Base):
        __tablename__ = "lesson_doc_ordered_version"
        __resource__ = "document_version"
        __allow_unmapped__ = True

        id = Column(Integer, primary_key=True)
        document_id = Column(
            Integer,
            ForeignKey("lesson_doc_ordered_document.id"),
            nullable=False,
        )
        version_index = Column(Integer, nullable=False)
        version_label = Column(String, nullable=False)
        body_snapshot = Column(String, nullable=False)
        document = relationship("Document", back_populates="version_history")

    # Step 3: Initialize the API with an in-memory engine.
    api = TigrblApp(engine=mem(async_=False))
    api.include_models([Document, DocumentVersion])
    init_result = api.initialize()
    if inspect.isawaitable(init_result):
        await init_result

    # Step 4: Mount the routes on an ASGI app.
    app = App()
    app.include_router(api.router)
    api.attach_diagnostics(prefix="", app=app)

    # Step 5: Start uvicorn and run the versioning workflow.
    port = pick_unique_port()
    base_url, server, task = await start_uvicorn(app, port=port)
    try:
        async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
            # Create the document that will own the versions.
            create_document = await client.post(
                "/document",
                json={"title": "Playbook", "body": "Draft"},
            )
            assert create_document.status_code == 201
            document_id = create_document.json()["id"]

            # Store the first version with index 1.
            await client.post(
                "/document_version",
                json={
                    "document_id": document_id,
                    "version_index": 1,
                    "version_label": "v1",
                    "body_snapshot": "Draft",
                },
            )

            # Update the document, then capture version 2.
            await client.patch(
                f"/document/{document_id}",
                json={"body": "Release"},
            )
            await client.post(
                "/document_version",
                json={
                    "document_id": document_id,
                    "version_index": 2,
                    "version_label": "v2",
                    "body_snapshot": "Release",
                },
            )

            # Fetch versions and confirm both are linked to the document.
            versions = await client.get("/document_version")
            assert versions.status_code == 200
            related = [
                item for item in versions.json() if item["document_id"] == document_id
            ]
            assert {item["version_index"] for item in related} == {1, 2}
    finally:
        # Stop uvicorn to keep the test process clean.
        await stop_uvicorn(server, task)
