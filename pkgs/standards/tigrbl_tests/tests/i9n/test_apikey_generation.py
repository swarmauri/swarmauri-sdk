import pytest
from httpx import ASGITransport, AsyncClient
from tigrbl import TigrblApp
from tigrbl.shortcuts.engine import mem
from tigrbl.orm.mixins import (
    Created,
    GUIDPk,
    KeyDigest,
    LastUsed,
    ValidityWindow,
)
from tigrbl import IO, F, S, acol
from tigrbl import Base
from tigrbl.types import Mapped, String


class ConcreteApiKey(Base, GUIDPk, Created, LastUsed, ValidityWindow, KeyDigest):
    """Concrete table for testing API key generation."""

    __abstract__ = False
    __resource__ = "apikey"
    __tablename__ = "apikeys_generation"

    label: Mapped[str] = acol(
        storage=S(String, nullable=False),
        field=F(required_in=("create",), constraints={"max_length": 120}),
        io=IO(in_verbs=("create",)),
    )


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_router_key_creation_requires_valid_payload(sync_db_session):
    """Posting without required fields yields an unprocessable entity response."""
    cfg, _ = sync_db_session

    app = TigrblApp(engine=mem(async_=False))
    app.include_tables([ConcreteApiKey])
    app.initialize()
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/apikey", json={})

    assert res.status_code == 422
