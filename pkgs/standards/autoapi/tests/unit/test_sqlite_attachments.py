import pytest
from autoapi.v3.autoapp import AutoApp
from autoapi.v3.engine.shortcuts import engine as make_engine, mem


def _db_names(conn):
    result = conn.exec_driver_sql("PRAGMA database_list")
    return {row[1] for row in result.fetchall()}


def test_initialize_sync_without_sqlite_attachments():
    eng = make_engine(mem(async_=False))
    api = AutoApp(engine=eng)
    api.initialize_sync()
    sql_engine, _ = eng.raw()
    with sql_engine.connect() as conn:
        assert _db_names(conn) == {"main"}


def test_initialize_sync_with_sqlite_attachments(tmp_path):
    eng = make_engine(mem(async_=False))
    attach_db = tmp_path / "logs.sqlite"
    attach_db.touch()
    api = AutoApp(engine=eng)
    api.initialize_sync(sqlite_attachments={"logs": str(attach_db)})
    sql_engine, _ = eng.raw()
    with sql_engine.connect() as conn:
        assert "logs" in _db_names(conn)


@pytest.mark.asyncio
async def test_initialize_async_without_sqlite_attachments():
    eng = make_engine(mem())
    api = AutoApp(engine=eng)
    await api.initialize_async()
    sql_engine, _ = eng.raw()
    async with sql_engine.connect() as conn:
        result = await conn.exec_driver_sql("PRAGMA database_list")
        names = {row[1] for row in result.fetchall()}
    assert names == {"main"}


@pytest.mark.asyncio
async def test_initialize_async_with_sqlite_attachments(tmp_path):
    eng = make_engine(mem())
    attach_db = tmp_path / "logs.sqlite"
    attach_db.touch()
    api = AutoApp(engine=eng)
    await api.initialize_async(sqlite_attachments={"logs": str(attach_db)})
    sql_engine, _ = eng.raw()
    async with sql_engine.connect() as conn:
        result = await conn.exec_driver_sql("PRAGMA database_list")
        names = {row[1] for row in result.fetchall()}
    assert "logs" in names
