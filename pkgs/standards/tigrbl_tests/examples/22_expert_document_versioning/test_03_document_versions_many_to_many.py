"""Example: association-model (many-to-many) document version links."""

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
async def test_document_versions_many_to_many_links() -> None:
    """Use an association model to link documents to version rows."""

    class Document(Base, GUIDPk):
        """Document model that links to versions through a join table."""

        __tablename__ = "lesson_doc_m2m_documents"
        __resource__ = "documents_m2m"
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

        version_links: Mapped[list["DocumentVersionLink"]] = relationship(
            "DocumentVersionLink",
            back_populates="document",
            cascade="all, delete-orphan",
        )

        @hook_ctx(ops="create", phase="POST_HANDLER")
        async def _create_initial_version(cls, ctx) -> None:
            """Create an initial version and link row after create."""

            db = ctx["db"]
            document = ctx["result"]
            version_row = DocumentVersion(
                version=document.version,
                title_snapshot=document.title,
                body_snapshot=document.body,
                created_at=dt.datetime.now(dt.timezone.utc),
            )
            link = DocumentVersionLink(document=document, version=version_row)
            db.add_all([version_row, link])
            db.flush()

        @hook_ctx(ops="update", phase="POST_HANDLER")
        async def _append_version(cls, ctx) -> None:
            """Append a new version and link row after updates."""

            db = ctx["db"]
            document = ctx["result"]
            document.version += 1
            version_row = DocumentVersion(
                version=document.version,
                title_snapshot=document.title,
                body_snapshot=document.body,
                created_at=dt.datetime.now(dt.timezone.utc),
            )
            link = DocumentVersionLink(document=document, version=version_row)
            db.add_all([version_row, link])
            db.flush()

    class DocumentVersion(Base, GUIDPk):
        """Snapshot rows that are shared through a join model."""

        __tablename__ = "lesson_doc_m2m_versions"
        __allow_unmapped__ = True

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

        document_links: Mapped[list["DocumentVersionLink"]] = relationship(
            "DocumentVersionLink",
            back_populates="version",
            cascade="all, delete-orphan",
        )

    class DocumentVersionLink(Base):
        """Association model that forms the many-to-many link."""

        __tablename__ = "lesson_doc_m2m_links"
        __allow_unmapped__ = True

        document_id: Mapped[UUID] = acol(
            storage=S(
                type_=PgUUID(as_uuid=True),
                fk=ForeignKeySpec(
                    target="lesson_doc_m2m_documents.id", on_delete="CASCADE"
                ),
                nullable=False,
                primary_key=True,
                index=True,
            ),
            field=F(py_type=UUID),
            io=IO(out_verbs=("read", "list")),
        )
        version_id: Mapped[UUID] = acol(
            storage=S(
                type_=PgUUID(as_uuid=True),
                fk=ForeignKeySpec(
                    target="lesson_doc_m2m_versions.id", on_delete="CASCADE"
                ),
                nullable=False,
                primary_key=True,
                index=True,
            ),
            field=F(py_type=UUID),
            io=IO(out_verbs=("read", "list")),
        )

        document: Mapped[Document] = relationship(
            "Document",
            back_populates="version_links",
            lazy="joined",
        )
        version: Mapped[DocumentVersion] = relationship(
            "DocumentVersion",
            back_populates="document_links",
            lazy="joined",
        )

    # Deployment: include all three models so tables are created.
    router = TigrblApp(engine=mem(async_=False))
    router.include_models([Document, DocumentVersion, DocumentVersionLink])
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
        # REST create: only call the Document endpoint.
        async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
            create = await client.post(
                "/documents_m2m",
                json={"title": "Guide", "body": "v1"},
            )
            assert create.status_code == 201
            document_id = create.json()["id"]

        # JSON-RPC update: still only Document.
        rpc = TigrblClient(f"{base_url}/rpc")
        update = await rpc.acall(
            "Document.update", params={"id": document_id, "body": "v2"}
        )
        assert update["version"] == 2
        await rpc.aclose()

        # Verification: confirm the association rows exist for each version.
        db, release = resolver.acquire(model=Document)
        try:
            links = (
                db.query(DocumentVersionLink)
                .filter_by(document_id=UUID(document_id))
                .all()
            )
        finally:
            release()
        assert len(links) == 2
    finally:
        await stop_uvicorn(server, task)
