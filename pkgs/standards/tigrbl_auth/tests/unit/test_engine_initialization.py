import pytest
from sqlalchemy import text
from tigrbl.engine import resolver as engine_resolver
from tigrbl_auth.routers.surface import surface_api


@pytest.mark.unit
async def test_engine_initialization(db_session):
    provider = engine_resolver.resolve_provider(api=surface_api)
    assert provider is not None
    result = await db_session.execute(text("PRAGMA foreign_keys"))
    assert result.scalar() == 1
