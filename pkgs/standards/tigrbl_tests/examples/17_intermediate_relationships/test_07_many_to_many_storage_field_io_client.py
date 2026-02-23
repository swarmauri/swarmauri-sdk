"""Pedagogical many-to-many relationship example via association table.

The example keeps everything explicit so readers can map the data model to
runtime behavior without hidden helper layers.
"""

from __future__ import annotations

import asyncio
import inspect
import socket

import httpx
import pytest
import uvicorn
from tigrbl_client import TigrblClient

from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.specs import F, IO, S, acol
from tigrbl.specs.storage_spec import ForeignKeySpec
from tigrbl.system import stop_uvicorn_server
from tigrbl.types import Mapped, PgUUID, String, UUID, relationship


@pytest.mark.asyncio
async def test_many_to_many_relationship_storage_field_io_client_experience() -> None:
    """Demonstrate many-to-many linking with both REST writes and RPC reads."""

    class Learner(Base, GUIDPk):
        """A person who can enroll in many workshops."""

        __tablename__ = "lesson_rel_sfic_learner"
        __resource__ = "learners_sfic"
        __allow_unmapped__ = True

        name: Mapped[str] = acol(
            storage=S(type_=String, nullable=False),
            field=F(py_type=str),
            io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
        )
        workshop_links: Mapped[list["LearnerWorkshop"]] = relationship(
            "LearnerWorkshop",
            back_populates="learner",
            cascade="all, delete-orphan",
            lazy="selectin",
        )

    class Workshop(Base, GUIDPk):
        """A class that can have many learners."""

        __tablename__ = "lesson_rel_sfic_workshop"
        __resource__ = "workshops_sfic"
        __allow_unmapped__ = True

        topic: Mapped[str] = acol(
            storage=S(type_=String, nullable=False),
            field=F(py_type=str),
            io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
        )
        learner_links: Mapped[list["LearnerWorkshop"]] = relationship(
            "LearnerWorkshop",
            back_populates="workshop",
            cascade="all, delete-orphan",
            lazy="selectin",
        )

    class LearnerWorkshop(Base, GUIDPk):
        """Association model that realizes the many-to-many relationship."""

        __tablename__ = "lesson_rel_sfic_learner_workshop"
        __resource__ = "learner_workshops_sfic"
        __allow_unmapped__ = True

        learner_id: Mapped[UUID] = acol(
            storage=S(
                type_=PgUUID(as_uuid=True),
                fk=ForeignKeySpec(
                    target="lesson_rel_sfic_learner.id", on_delete="CASCADE"
                ),
                nullable=False,
                index=True,
            ),
            field=F(py_type=UUID),
            io=IO(in_verbs=("create",), out_verbs=("read", "list")),
        )
        workshop_id: Mapped[UUID] = acol(
            storage=S(
                type_=PgUUID(as_uuid=True),
                fk=ForeignKeySpec(
                    target="lesson_rel_sfic_workshop.id", on_delete="CASCADE"
                ),
                nullable=False,
                index=True,
            ),
            field=F(py_type=UUID),
            io=IO(in_verbs=("create",), out_verbs=("read", "list")),
        )
        role: Mapped[str] = acol(
            storage=S(type_=String, nullable=False),
            field=F(py_type=str),
            io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
        )

        learner: Mapped[Learner] = relationship(
            "Learner", back_populates="workshop_links", lazy="joined"
        )
        workshop: Mapped[Workshop] = relationship(
            "Workshop", back_populates="learner_links", lazy="joined"
        )

    api = TigrblApp(engine=mem(async_=False))
    api.include_models([Learner, Workshop, LearnerWorkshop])
    init_result = api.initialize()
    if inspect.isawaitable(init_result):
        await init_result
    api.mount_jsonrpc(prefix="/rpc")

    app = TigrblApp()
    app.include_router(api.router)
    api.attach_diagnostics(prefix="", app=app)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        port = int(sock.getsockname()[1])
    base_url = f"http://127.0.0.1:{port}"
    server = uvicorn.Server(
        uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    )
    task = asyncio.create_task(server.serve(), name=f"uvicorn-{port}")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            deadline = asyncio.get_event_loop().time() + 5.0
            while True:
                try:
                    response = await client.get(f"{base_url}/healthz")
                    if response.status_code < 500:
                        break
                except httpx.HTTPError:
                    pass
                if asyncio.get_event_loop().time() > deadline:
                    raise RuntimeError("Server did not become healthy in time.")
                await asyncio.sleep(0.1)

        # REST calls create base entities and the association rows.
        async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
            learner_response = await client.post(
                "/learners_sfic", json={"name": "Imani"}
            )
            workshop_response = await client.post(
                "/workshops_sfic", json={"topic": "API Design Fundamentals"}
            )
            assert learner_response.status_code == 201
            assert workshop_response.status_code == 201

            learner_id = learner_response.json()["id"]
            workshop_id = workshop_response.json()["id"]

            link_response = await client.post(
                "/learner_workshops_sfic",
                json={
                    "learner_id": learner_id,
                    "workshop_id": workshop_id,
                    "role": "participant",
                },
            )
            assert link_response.status_code == 201

        # JSON-RPC read confirms the relationship row is queryable over RPC.
        rpc = TigrblClient(f"{base_url}/rpc")
        links = await rpc.acall("LearnerWorkshop.list", params={})
        assert any(
            row["learner_id"] == learner_id
            and row["workshop_id"] == workshop_id
            and row["role"] == "participant"
            for row in links
        )

        await rpc.aclose()
    finally:
        await stop_uvicorn_server(server, task)
