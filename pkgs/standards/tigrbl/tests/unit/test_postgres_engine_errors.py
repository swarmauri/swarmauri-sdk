import pytest
from sqlalchemy import text

from tigrbl.engine.builders import async_postgres_engine


@pytest.mark.asyncio
async def test_async_postgres_engine_connection_error(monkeypatch):
    monkeypatch.setenv("PGHOST", "localhost")
    monkeypatch.setenv("PGPORT", "65432")
    eng, Session = async_postgres_engine()

    with pytest.raises(RuntimeError, match="Failed to connect to database"):
        async with Session() as session:
            await session.run_sync(lambda s: s.execute(text("select 1")))

    await eng.dispose()
