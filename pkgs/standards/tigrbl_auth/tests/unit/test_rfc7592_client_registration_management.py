"""Tests for RFC 7592 client management operations."""

import uuid

import pytest

from tigrbl_auth import rfc7592
from tigrbl_auth.orm import Client


def test_rfc7592_spec_url() -> None:
    """Module exports the specification URL."""
    assert rfc7592.RFC7592_SPEC_URL.endswith("7592")


@pytest.mark.asyncio
@pytest.mark.xfail(reason="client management endpoint not available", strict=False)
async def test_update_and_delete_client_via_server(async_client, db_session):
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
    fetched = await async_client.get(f"/client/{client_id}")
    assert fetched.status_code == 200
    uris = fetched.json()["redirect_uris"]
    if isinstance(uris, str):
        uris = [uris]
    assert "https://b.example/cb" in uris
    await Client.handlers.delete.core(
        {"payload": {"ident": str(client_id)}, "db": db_session}
    )
    after = await async_client.get(f"/client/{client_id}")
    assert after.status_code == 404
