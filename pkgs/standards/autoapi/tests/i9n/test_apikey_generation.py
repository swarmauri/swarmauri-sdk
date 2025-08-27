import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from autoapi.v3 import AutoAPI, Base
from autoapi.v3.tables import ApiKey


class ConcreteApiKey(ApiKey):
    """Concrete table for testing API key generation."""

    __abstract__ = False


# Ensure hooks register under expected model name
ConcreteApiKey.__name__ = "ApiKey"


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_api_key_creation_returns_raw_key(sync_db_session):
    """Creating an API key returns the raw key once."""
    _, get_sync_db = sync_db_session
    Base.metadata.clear()
    api = AutoAPI(base=Base, include={ConcreteApiKey}, get_db=get_sync_db)
    api.initialize_sync()

    app = FastAPI()
    app.include_router(api.router)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api_key", json={"label": "test"})

    assert res.status_code == 201
    data = res.json()
    assert data["label"] == "test"
    assert "api_key" in data and data["api_key"]
    assert "digest" in data and data["digest"]
