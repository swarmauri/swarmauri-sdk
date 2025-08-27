import pytest
from autoapi.v3.types import App
from httpx import ASGITransport, AsyncClient

from autoapi.v3 import AutoAPI, Base
from autoapi.v3.tables import ApiKey


class ConcreteApiKey(ApiKey):
    """Concrete table for testing API key generation."""

    __abstract__ = False
    __resource__ = "apikey"


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_api_key_creation_requires_valid_payload(sync_db_session):
    """Posting without required fields yields a conflict response."""
    _, get_sync_db = sync_db_session
    Base.metadata.clear()

    app = App()
    api = AutoAPI(app=app, get_db=get_sync_db)
    api.include_models([ConcreteApiKey])
    api.initialize_sync()
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/apikey", json={})

    assert res.status_code == 409
