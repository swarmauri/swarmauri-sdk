import pytest
from autoapi.v3.types import App, Mapped, String
from httpx import ASGITransport, AsyncClient

from autoapi.v3 import AutoApp
from autoapi.v3.orm.mixins import (
    Created,
    GUIDPk,
    KeyDigest,
    LastUsed,
    ValidityWindow,
)
from autoapi.v3.orm.tables._base import Base
from autoapi.v3.specs import F, S, acol


class ConcreteApiKey(Base, GUIDPk, Created, LastUsed, ValidityWindow, KeyDigest):
    """Concrete table for testing API key generation."""

    __abstract__ = False
    __resource__ = "apikey"
    __tablename__ = "apikeys_generation"

    label: Mapped[str] = acol(
        storage=S(String, nullable=False),
        field=F(constraints={"max_length": 120}),
    )


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_api_key_creation_requires_valid_payload(sync_db_session):
    """Posting without required fields yields an unprocessable entity response."""
    _, get_sync_db = sync_db_session

    app = App()
    api = AutoApp(get_db=get_sync_db)
    api.include_models([ConcreteApiKey])
    api.initialize()
    app.include_router(api.router)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/apikey", json={})

    assert res.status_code == 422
