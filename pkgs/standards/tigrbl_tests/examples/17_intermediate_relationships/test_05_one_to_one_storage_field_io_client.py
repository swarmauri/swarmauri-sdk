"""Pedagogical one-to-one relationship example across storage, field, IO, and clients.

This example intentionally shows the full flow:
- relationship modeling with ``relationship``.
- column declarations with ``S`` (storage), ``F`` (field), and ``IO``.
- uvicorn-hosted app startup.
- both REST and JSON-RPC client calls against the same running server.
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
async def test_one_to_one_relationship_storage_field_io_client_experience() -> None:
    """Demonstrate a one-to-one model with REST + JSON-RPC client interactions."""

    class Account(Base, GUIDPk):
        """Parent record in a one-to-one relationship."""

        __tablename__ = "lesson_rel_sfic_account"
        __resource__ = "accounts_sfic"
        __allow_unmapped__ = True

        display_name: Mapped[str] = acol(
            storage=S(type_=String, nullable=False),
            field=F(py_type=str),
            io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
        )
        profile: Mapped["Profile"] = relationship(
            "Profile",
            back_populates="account",
            uselist=False,
            cascade="all, delete-orphan",
            lazy="selectin",
        )

    class Profile(Base, GUIDPk):
        """Child record that is uniquely linked to one account."""

        __tablename__ = "lesson_rel_sfic_profile"
        __resource__ = "profiles_sfic"
        __allow_unmapped__ = True

        account_id: Mapped[UUID] = acol(
            storage=S(
                type_=PgUUID(as_uuid=True),
                fk=ForeignKeySpec(
                    target="lesson_rel_sfic_account.id", on_delete="CASCADE"
                ),
                unique=True,
                nullable=False,
            ),
            field=F(py_type=UUID),
            io=IO(in_verbs=("create",), out_verbs=("read", "list")),
        )
        bio: Mapped[str] = acol(
            storage=S(type_=String, nullable=False),
            field=F(py_type=str),
            io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
        )
        account: Mapped[Account] = relationship(
            "Account", back_populates="profile", lazy="joined"
        )

    # Build the Tigrbl API from model metadata.
    router = TigrblApp(engine=mem(async_=False))
    router.include_models([Account, Profile])
    init_result = router.initialize()
    if inspect.isawaitable(init_result):
        await init_result
    router.mount_jsonrpc(prefix="/rpc")

    app = TigrblApp()
    app.include_router(router.router)
    router.attach_diagnostics(prefix="", app=app)

    # Start a real uvicorn server so the example mirrors production usage.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        port = int(sock.getsockname()[1])
    base_url = f"http://127.0.0.1:{port}"
    server = uvicorn.Server(
        uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    )
    task = asyncio.create_task(server.serve(), name=f"uvicorn-{port}")

    try:
        # Wait until diagnostics endpoint reports healthy.
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

        # REST call: create the account.
        async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
            create_account = await client.post(
                "/accounts_sfic", json={"display_name": "Mina"}
            )
            assert create_account.status_code == 201
            account_id = create_account.json()["id"]

        # JSON-RPC call: create the related profile.
        rpc = TigrblClient(f"{base_url}/rpc")
        profile = await rpc.acall(
            "Profile.create",
            params={"account_id": account_id, "bio": "Writes API docs."},
        )

        assert profile["account_id"] == account_id

        # REST verification: read the profile list and confirm exactly one row for this account.
        async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
            profiles = await client.get("/profiles_sfic")
            assert profiles.status_code == 200
            linked_profiles = [
                item for item in profiles.json() if item["account_id"] == account_id
            ]
            assert len(linked_profiles) == 1

        await rpc.aclose()
    finally:
        # Always stop the server task so no background process leaks.
        await stop_uvicorn_server(server, task)
