"""Pedagogical one-to-many relationship example with REST and JSON-RPC clients.

This walkthrough demonstrates a complete user journey:
1. define data and relationship semantics with storage/field/IO specs,
2. run the app with uvicorn,
3. write through REST,
4. read through JSON-RPC.
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
async def test_one_to_many_relationship_storage_field_io_client_experience() -> None:
    """Show one project owning many tasks, validated through both API styles."""

    class Project(Base, GUIDPk):
        """Parent model that owns a collection of tasks."""

        __tablename__ = "lesson_rel_sfic_project"
        __resource__ = "projects_sfic"
        __allow_unmapped__ = True

        name: Mapped[str] = acol(
            storage=S(type_=String, nullable=False),
            field=F(py_type=str),
            io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
        )
        tasks: Mapped[list["Task"]] = relationship(
            "Task",
            back_populates="project",
            cascade="all, delete-orphan",
            lazy="selectin",
        )

    class Task(Base, GUIDPk):
        """Child model: many tasks can point to the same project."""

        __tablename__ = "lesson_rel_sfic_task"
        __resource__ = "tasks_sfic"
        __allow_unmapped__ = True

        project_id: Mapped[UUID] = acol(
            storage=S(
                type_=PgUUID(as_uuid=True),
                fk=ForeignKeySpec(
                    target="lesson_rel_sfic_project.id", on_delete="CASCADE"
                ),
                nullable=False,
                index=True,
            ),
            field=F(py_type=UUID),
            io=IO(in_verbs=("create",), out_verbs=("read", "list")),
        )
        title: Mapped[str] = acol(
            storage=S(type_=String, nullable=False),
            field=F(py_type=str),
            io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
        )
        project: Mapped[Project] = relationship(
            "Project", back_populates="tasks", lazy="joined"
        )

    api = TigrblApp(engine=mem(async_=False))
    api.include_models([Project, Task])
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

        async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
            create_project = await client.post(
                "/projects_sfic", json={"name": "Docs Refresh"}
            )
            assert create_project.status_code == 201
            project_id = create_project.json()["id"]

            # REST writes: add two task rows that both point to one project.
            create_first_task = await client.post(
                "/tasks_sfic",
                json={"project_id": project_id, "title": "Outline chapters"},
            )
            create_second_task = await client.post(
                "/tasks_sfic",
                json={"project_id": project_id, "title": "Add examples"},
            )
            assert create_first_task.status_code == 201
            assert create_second_task.status_code == 201

        # JSON-RPC reads: list tasks and confirm one-to-many fan-out.
        rpc = TigrblClient(f"{base_url}/rpc")
        listed_tasks = await rpc.acall("Task.list", params={})
        related_task_titles = sorted(
            [item["title"] for item in listed_tasks if item["project_id"] == project_id]
        )
        assert related_task_titles == ["Add examples", "Outline chapters"]

        await rpc.aclose()
    finally:
        await stop_uvicorn_server(server, task)
