import pytest
from tigrbl import TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.types import Mapped, String
from httpx import ASGITransport, AsyncClient

from tigrbl.orm.mixins import (
    Created,
    GUIDPk,
    KeyDigest,
    LastUsed,
    ValidityWindow,
)
from tigrbl.orm.tables._base import Base
from tigrbl.specs import F, IO, S, acol


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

<<<<<<< HEAD
    app = TigrblApp(engine=mem(async_=False))
    app.include_tables([ConcreteApiKey])
    app.initialize()
=======
    app = TigrblApp()
    router = TigrblApp(get_db=get_sync_db)
    router.include_models([ConcreteApiKey])
    router.initialize()
    app.include_router(router.router)
>>>>>>> a8f183f2e9f9d711015dec095ba64838fae67a3c
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/apikey", json={})

    assert res.status_code == 422
