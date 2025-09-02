import pytest
from httpx import ASGITransport, AsyncClient

from autoapi.v3 import AutoApp
from autoapi.v3.orm.tables import ApiKey


class ConcreteApiKey(ApiKey):
    """Concrete table for testing API key generation."""

    __abstract__ = False
    __resource__ = "apikey"
    __tablename__ = "apikeys_generation"


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_api_key_creation_requires_valid_payload(sync_db_session):
    """Posting without required fields yields an unprocessable entity response."""
    _, _ = sync_db_session

    app = AutoApp()
    app.include_models([ConcreteApiKey])
    app.initialize_sync()
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/apikey", json={})

    assert res.status_code == 422
