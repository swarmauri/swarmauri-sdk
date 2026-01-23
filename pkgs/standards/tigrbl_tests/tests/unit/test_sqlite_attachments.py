import pytest
from tigrbl import TigrblApp


def _db_names(conn):
    result = conn.exec_driver_sql("PRAGMA database_list")
    return {row[1] for row in result.fetchall()}


def test_initialize_sync_without_sqlite_attachments(sync_db_session):
    engine, get_db = sync_db_session
    api = TigrblApp(get_db=get_db)
    api.initialize()
    with engine.connect() as conn:
        assert _db_names(conn) == {"main"}
        fk = conn.exec_driver_sql("PRAGMA foreign_keys").scalar()
        assert fk == 1


def test_initialize_sync_with_sqlite_attachments(sync_db_session, tmp_path):
    engine, get_db = sync_db_session
    attach_db = tmp_path / "logs.sqlite"
    attach_db.touch()
    api = TigrblApp(get_db=get_db)
    api.initialize(sqlite_attachments={"logs": str(attach_db)})
    with engine.connect() as conn:
        assert "logs" in _db_names(conn)
        fk = conn.exec_driver_sql("PRAGMA foreign_keys").scalar()
        assert fk == 1


@pytest.mark.asyncio
async def test_initialize_async_without_sqlite_attachments(async_db_session):
    engine, get_db = async_db_session
    api = TigrblApp(get_db=get_db)
    await api.initialize()
    async with engine.connect() as conn:
        result = await conn.exec_driver_sql("PRAGMA database_list")
        names = {row[1] for row in result.fetchall()}
        fk = await conn.exec_driver_sql("PRAGMA foreign_keys")
        assert fk.scalar() == 1
    assert names == {"main"}


@pytest.mark.asyncio
async def test_initialize_async_with_sqlite_attachments(async_db_session, tmp_path):
    engine, get_db = async_db_session
    attach_db = tmp_path / "logs.sqlite"
    attach_db.touch()
    api = TigrblApp(get_db=get_db)
    await api.initialize(sqlite_attachments={"logs": str(attach_db)})
    async with engine.connect() as conn:
        result = await conn.exec_driver_sql("PRAGMA database_list")
        names = {row[1] for row in result.fetchall()}
        fk = await conn.exec_driver_sql("PRAGMA foreign_keys")
        assert fk.scalar() == 1
    assert "logs" in names
