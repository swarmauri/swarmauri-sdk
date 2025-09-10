import pytest
from tigrbl import TigrblApp
from tigrbl.engine.shortcuts import engine as build_engine, mem


def _db_names(conn):
    result = conn.exec_driver_sql("PRAGMA database_list")
    return {row[1] for row in result.fetchall()}


def test_initialize_sync_with_sqlite_attachments(tmp_path):
    eng = build_engine(mem(async_=False))
    attach_db = tmp_path / "logs.sqlite"
    attach_db.touch()
    api = TigrblApp(engine=eng)
    api.initialize(sqlite_attachments={"logs": str(attach_db)})
    sql_eng, _ = eng.raw()
    with sql_eng.connect() as conn:
        assert "logs" in _db_names(conn)
        fk = conn.exec_driver_sql("PRAGMA foreign_keys").scalar()
        assert fk == 1


@pytest.mark.asyncio
async def test_initialize_async_with_sqlite_attachments(tmp_path):
    eng = build_engine(mem())
    attach_db = tmp_path / "logs.sqlite"
    attach_db.touch()
    api = TigrblApp(engine=eng)
    await api.initialize(sqlite_attachments={"logs": str(attach_db)})
    sql_eng, _ = eng.raw()
    async with sql_eng.connect() as conn:
        names = await conn.run_sync(_db_names)
        fk = await conn.exec_driver_sql("PRAGMA foreign_keys")
        assert fk.scalar() == 1
    assert "logs" in names
