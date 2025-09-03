import pytest
from autoapi.v3.autoapp import AutoApp


def _db_names(conn):
    result = conn.exec_driver_sql("PRAGMA database_list")
    return {row[1] for row in result.fetchall()}


def test_initialize_sync_without_sqlite_attachments(sync_db_session):
    engine, get_db = sync_db_session
    api = AutoApp(get_db=get_db)
    api.initialize()
    with engine.connect() as conn:
        assert _db_names(conn) == {"main"}


def test_initialize_sync_with_sqlite_attachments(sync_db_session, tmp_path):
    engine, get_db = sync_db_session
    attach_db = tmp_path / "logs.sqlite"
    attach_db.touch()
    api = AutoApp(get_db=get_db)
    api.initialize(sqlite_attachments={"logs": str(attach_db)})
    with engine.connect() as conn:
        assert "logs" in _db_names(conn)


@pytest.mark.asyncio
async def test_initialize_async_without_sqlite_attachments(async_db_session):
    engine, get_db = async_db_session
    api = AutoApp(get_db=get_db)
    await api.initialize()
    async with engine.connect() as conn:
        result = await conn.exec_driver_sql("PRAGMA database_list")
        names = {row[1] for row in result.fetchall()}
    assert names == {"main"}


@pytest.mark.asyncio
async def test_initialize_async_with_sqlite_attachments(async_db_session, tmp_path):
    engine, get_db = async_db_session
    attach_db = tmp_path / "logs.sqlite"
    attach_db.touch()
    api = AutoApp(get_db=get_db)
    await api.initialize(sqlite_attachments={"logs": str(attach_db)})
    async with engine.connect() as conn:
        result = await conn.exec_driver_sql("PRAGMA database_list")
        names = {row[1] for row in result.fetchall()}
    assert "logs" in names
