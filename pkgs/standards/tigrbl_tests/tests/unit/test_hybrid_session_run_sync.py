import pytest

from tigrbl.engine.builders import async_sqlite_engine
from sqlalchemy import text
from sqlalchemy.orm import Session as SyncSession


@pytest.mark.asyncio
async def test_hybrid_session_run_sync_provides_session():
    eng, Session = async_sqlite_engine()
    async with Session() as db:

        def _check(sess: SyncSession) -> None:
            assert isinstance(sess, SyncSession)
            # accessing Session.get should not raise
            sess.get  # noqa: B018 - attribute access for test

        await db.run_sync(_check)
    await eng.dispose()


@pytest.mark.asyncio
async def test_async_sqlite_engine_defaults_to_memory_url():
    eng, Session = async_sqlite_engine()
    try:
        assert str(eng.url) == "sqlite+aiosqlite:///:memory:"

        async with Session() as db:

            def _create_and_insert(sess: SyncSession) -> None:
                sess.execute(text("CREATE TABLE sample (id INTEGER PRIMARY KEY)"))
                sess.execute(text("INSERT INTO sample (id) VALUES (1)"))

            await db.run_sync(_create_and_insert)
            await db.commit()

        async with Session() as db:

            def _count_rows(sess: SyncSession) -> int:
                return int(
                    sess.execute(text("SELECT COUNT(*) FROM sample")).scalar_one()
                )

            assert await db.run_sync(_count_rows) == 1
    finally:
        await eng.dispose()
