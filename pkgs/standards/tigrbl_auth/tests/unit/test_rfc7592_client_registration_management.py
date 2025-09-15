"""Tests for RFC 7592 client management operations."""

import uuid

import pytest

from tigrbl_auth import rfc7592
from tigrbl_auth.orm import Client
from sqlalchemy.exc import NoResultFound


def test_rfc7592_spec_url() -> None:
    """Module exports the specification URL."""
    assert rfc7592.RFC7592_SPEC_URL.endswith("7592")


@pytest.mark.asyncio
async def test_update_and_delete_client_via_server(db_session):
    client = Client.new(
        tenant_id=uuid.UUID("FFFFFFFF-0000-0000-0000-000000000000"),
        client_id=str(uuid.uuid4()),
        client_secret="secret",
        redirects=["https://a.example/cb"],
    )
    db_session.add(client)
    await db_session.commit()
    client_id = client.id
    await Client.handlers.update.core(
        {
            "payload": {
                "ident": str(client_id),
                "redirect_uris": "https://b.example/cb",
            },
            "db": db_session,
        }
    )
    fetched = await Client.handlers.read.core(
        {"payload": {"id": str(client_id)}, "db": db_session}
    )
    assert fetched is not None
    uris = fetched.redirect_uris
    if isinstance(uris, str):
        uris = uris.split()
    assert "https://b.example/cb" in uris
    await Client.handlers.delete.core(
        {"payload": {"ident": str(client_id)}, "db": db_session}
    )
    with pytest.raises(NoResultFound):
        await Client.handlers.read.core(
            {"payload": {"id": str(client_id)}, "db": db_session}
        )
