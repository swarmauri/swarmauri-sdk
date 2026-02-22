"""Example: one-to-one current version pointer plus version history."""

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
async def test_document_versions_one_to_one_current_pointer() -> None:
    """Maintain a one-to-one current_version alongside a history list."""

    class Document(Base, GUIDPk):
        """Document model with a one-to-one pointer to the latest version."""

        __tablename__ = "lesson_doc_oto_documents"
        __resource__ = "documents_oto"
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
        current_version_id: Mapped[UUID | None] = acol(
            storage=S(
                type_=PgUUID(as_uuid=True),
                fk=ForeignKeySpec(target="lesson_doc_oto_versions.id"),
                nullable=True,
            ),
            field=F(py_type=UUID),
            io=IO(out_verbs=("read", "list")),
        )

        version_history: Mapped[list["DocumentVersion"]] = relationship(
            "DocumentVersion",
            back_populates="document",
            foreign_keys="DocumentVersion.document_id",
            lazy="selectin",
            cascade="all, delete-orphan",
        )
        current_version: Mapped["DocumentVersion"] = relationship(
            "DocumentVersion",
            foreign_keys="Document.current_version_id",
            post_update=True,
            uselist=False,
            lazy="joined",
        )

        @hook_ctx(ops="create", phase="POST_HANDLER")
        async def _create_initial_version(cls, ctx) -> None:
            """Create the first version and set it as current."""

            db = ctx["db"]
            document = ctx["result"]
            version_row = DocumentVersion(
                document_id=document.id,
                version=document.version,
                title_snapshot=document.title,
                body_snapshot=document.body,
                created_at=dt.datetime.now(dt.timezone.utc),
            )
            document.current_version = version_row
            document.version_history.append(version_row)
            db.add(version_row)
            db.flush()

        @hook_ctx(ops="update", phase="POST_HANDLER")
        async def _advance_current_version(cls, ctx) -> None:
            """Roll the current_version pointer forward after updates."""

            db = ctx["db"]
            document = ctx["result"]
            document.version += 1
            version_row = DocumentVersion(
                document_id=document.id,
                version=document.version,
                title_snapshot=document.title,
                body_snapshot=document.body,
                created_at=dt.datetime.now(dt.timezone.utc),
            )
            document.current_version = version_row
            document.version_history.append(version_row)
            db.add(version_row)
            db.flush()

    class DocumentVersion(Base, GUIDPk):
        """Version snapshots that also serve as the current pointer."""

        __tablename__ = "lesson_doc_oto_versions"
        __allow_unmapped__ = True

        document_id: Mapped[UUID] = acol(
            storage=S(
                type_=PgUUID(as_uuid=True),
                fk=ForeignKeySpec(
                    target="lesson_doc_oto_documents.id", on_delete="CASCADE"
                ),
                nullable=False,
                index=True,
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
            foreign_keys="DocumentVersion.document_id",
            lazy="joined",
        )

    # Deployment: register models and JSON-RPC routes.
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
        # REST create: Document only.
        async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
            create = await client.post(
                "/documents_oto",
                json={"title": "Spec", "body": "v1"},
            )
            assert create.status_code == 201
            document_id = create.json()["id"]

        # JSON-RPC update: Document only.
        rpc = TigrblClient(f"{base_url}/rpc")
        update = await rpc.acall(
            "Document.update", params={"id": document_id, "body": "v2"}
        )
        assert update["version"] == 2
        await rpc.aclose()

        # Verification: current_version_id should match the newest row.
        db, release = resolver.acquire(model=Document)
        try:
            latest = (
                db.query(DocumentVersion)
                .filter_by(document_id=UUID(document_id))
                .order_by(DocumentVersion.version.desc())
                .first()
            )
            document = db.query(Document).filter_by(id=UUID(document_id)).one()
        finally:
            release()
        assert latest is not None
        assert document.current_version_id == latest.id
    finally:
        await stop_uvicorn(server, task)
