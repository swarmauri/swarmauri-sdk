import pytest

from tigrbl.engine.builders import async_sqlite_engine
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
