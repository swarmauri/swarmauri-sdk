"""Example: self-referential version lineage for document history."""

from __future__ import annotations

import datetime as dt
import inspect

import httpx
import pytest
from tigrbl_client import TigrblClient

from examples._support import pick_unique_port, start_uvicorn, stop_uvicorn
from tigrbl import Base, TigrblApp, hook_ctx
from tigrbl.engine import resolver
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.specs import F, IO, S, acol
from tigrbl.specs.storage_spec import ForeignKeySpec
from tigrbl.types import (
    Integer,
    Mapped,
    PgUUID,
    String,
    TZDateTime,
    UUID,
    relationship,
)


@pytest.mark.asyncio
async def test_document_versions_self_referential_lineage() -> None:
    """Chain versions together using a self-referential relationship."""

    class Document(Base, GUIDPk):
        """Document with version history that tracks parent-child lineage."""

        __tablename__ = "lesson_doc_self_documents"
        __resource__ = "documents_self"
        __allow_unmapped__ = True

        title: Mapped[str] = acol(
            storage=S(type_=String, nullable=False),
            field=F(py_type=str),
            io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
        )
        body: Mapped[str] = acol(
            storage=S(type_=String, nullable=False),
            field=F(py_type=str),
            io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
        )
        version: Mapped[int] = acol(
            storage=S(type_=Integer, nullable=False, default=1),
            field=F(py_type=int),
            io=IO(out_verbs=("read", "list")),
        )

        version_history: Mapped[list["DocumentVersion"]] = relationship(
            "DocumentVersion",
            back_populates="document",
            lazy="selectin",
            cascade="all, delete-orphan",
        )

        @hook_ctx(ops="create", phase="POST_HANDLER")
        async def _create_initial_version(cls, ctx) -> None:
            """Insert the first version with no parent."""

            db = ctx["db"]
            document = ctx["result"]
            version_row = DocumentVersion(
                document_id=document.id,
                version=document.version,
                title_snapshot=document.title,
                body_snapshot=document.body,
                created_at=dt.datetime.now(dt.timezone.utc),
            )
            document.version_history.append(version_row)
            db.add(version_row)
            db.flush()

        @hook_ctx(ops="update", phase="POST_HANDLER")
        async def _append_version(cls, ctx) -> None:
            """Create a new version that references the previous one."""

            db = ctx["db"]
            document = ctx["result"]
            previous = (
                db.query(DocumentVersion)
                .filter_by(document_id=document.id)
                .order_by(DocumentVersion.version.desc())
                .first()
            )
            document.version += 1
            version_row = DocumentVersion(
                document_id=document.id,
                version=document.version,
                title_snapshot=document.title,
                body_snapshot=document.body,
                created_at=dt.datetime.now(dt.timezone.utc),
                parent_version=previous,
            )
            document.version_history.append(version_row)
            db.add(version_row)
            db.flush()

    class DocumentVersion(Base, GUIDPk):
        """Version snapshots linked to both a document and a parent version."""

        __tablename__ = "lesson_doc_self_versions"
        __allow_unmapped__ = True

        document_id: Mapped[UUID] = acol(
            storage=S(
                type_=PgUUID(as_uuid=True),
                fk=ForeignKeySpec(
                    target="lesson_doc_self_documents.id", on_delete="CASCADE"
                ),
                nullable=False,
                index=True,
            ),
            field=F(py_type=UUID),
            io=IO(out_verbs=("read", "list")),
        )
        parent_version_id: Mapped[UUID | None] = acol(
            storage=S(
                type_=PgUUID(as_uuid=True),
                fk=ForeignKeySpec(target="lesson_doc_self_versions.id"),
                nullable=True,
            ),
            field=F(py_type=UUID),
            io=IO(out_verbs=("read", "list")),
        )
        version: Mapped[int] = acol(
            storage=S(type_=Integer, nullable=False),
            field=F(py_type=int),
            io=IO(out_verbs=("read", "list")),
        )
        title_snapshot: Mapped[str] = acol(
            storage=S(type_=String, nullable=False),
            field=F(py_type=str),
            io=IO(out_verbs=("read", "list")),
        )
        body_snapshot: Mapped[str] = acol(
            storage=S(type_=String, nullable=False),
            field=F(py_type=str),
            io=IO(out_verbs=("read", "list")),
        )
        created_at: Mapped[dt.datetime] = acol(
            storage=S(
                type_=TZDateTime,
                nullable=False,
                default=lambda: dt.datetime.now(dt.timezone.utc),
            ),
            field=F(py_type=dt.datetime),
            io=IO(out_verbs=("read", "list")),
        )

        document: Mapped[Document] = relationship(
            "Document",
            back_populates="version_history",
            lazy="joined",
        )
        parent_version: Mapped["DocumentVersion | None"] = relationship(
            "DocumentVersion",
            remote_side="DocumentVersion.id",
            back_populates="child_versions",
        )
        child_versions: Mapped[list["DocumentVersion"]] = relationship(
            "DocumentVersion",
            back_populates="parent_version",
            cascade="all, delete-orphan",
        )

    # Deployment: include models so DDL includes the self-referential table.
    router = TigrblApp(engine=mem(async_=False))
    router.include_models([Document, DocumentVersion])
    init_result = router.initialize()
    if inspect.isawaitable(init_result):
        await init_result
    router.mount_jsonrpc(prefix="/rpc")

    app = TigrblApp()
    app.include_router(router.router)
    router.attach_diagnostics(prefix="", app=app)

    port = pick_unique_port()
    base_url, server, task = await start_uvicorn(app, port=port)
    try:
        # REST create: only call Document.
        async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
            create = await client.post(
                "/documents_self",
                json={"title": "Chain", "body": "v1"},
            )
            assert create.status_code == 201
            document_id = create.json()["id"]

        # JSON-RPC update: still Document only.
        rpc = TigrblClient(f"{base_url}/rpc")
        update = await rpc.acall(
            "Document.update", params={"id": document_id, "body": "v2"}
        )
        assert update["version"] == 2
        await rpc.aclose()

        # Verification: the newest version should reference the previous one.
        db, release = resolver.acquire(model=Document)
        try:
            versions = (
                db.query(DocumentVersion)
                .filter_by(document_id=UUID(document_id))
                .order_by(DocumentVersion.version)
                .all()
            )
        finally:
            release()
        assert len(versions) == 2
        assert versions[1].parent_version_id == versions[0].id
    finally:
        await stop_uvicorn(server, task)
