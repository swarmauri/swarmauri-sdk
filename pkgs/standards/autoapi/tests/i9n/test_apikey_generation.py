import pytest
from autoapi.v3.types import App
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
    _, eng = sync_db_session

    app = App()
    api = AutoApp(engine=eng)
    api.include_models([ConcreteApiKey])
    api.initialize_sync()
    app.include_router(api.router)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/apikey", json={})

    assert res.status_code == 422
