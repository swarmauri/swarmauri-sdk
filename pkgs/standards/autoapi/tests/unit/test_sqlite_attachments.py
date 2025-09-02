import pytest

from autoapi.v3.autoapp import AutoApp
from autoapi.v3.engine import resolver as _resolver
from autoapi.v3.engine.shortcuts import mem


def _db_names(conn):
    result = conn.exec_driver_sql("PRAGMA database_list")
    return {row[1] for row in result.fetchall()}


def test_initialize_sync_without_sqlite_attachments():
    api = AutoApp(engine=mem(async_=False))
    api.initialize_sync()
    prov = _resolver.resolve_provider(api=api)
    engine, _ = prov.ensure()
    with engine.connect() as conn:
        assert _db_names(conn) == {"main"}


def test_initialize_sync_with_sqlite_attachments(tmp_path):
    attach_db = tmp_path / "logs.sqlite"
    attach_db.touch()
    api = AutoApp(engine=mem(async_=False))
    api.initialize_sync(sqlite_attachments={"logs": str(attach_db)})
    prov = _resolver.resolve_provider(api=api)
    engine, _ = prov.ensure()
    with engine.connect() as conn:
        assert "logs" in _db_names(conn)


@pytest.mark.asyncio
async def test_initialize_async_without_sqlite_attachments():
    api = AutoApp(engine=mem())
    await api.initialize_async()
    prov = _resolver.resolve_provider(api=api)
    engine, _ = prov.ensure()
    async with engine.connect() as conn:
        result = await conn.exec_driver_sql("PRAGMA database_list")
        names = {row[1] for row in result.fetchall()}
    assert names == {"main"}


@pytest.mark.asyncio
async def test_initialize_async_with_sqlite_attachments(tmp_path):
    attach_db = tmp_path / "logs.sqlite"
    attach_db.touch()
    api = AutoApp(engine=mem())
    await api.initialize_async(sqlite_attachments={"logs": str(attach_db)})
    prov = _resolver.resolve_provider(api=api)
    engine, _ = prov.ensure()
    async with engine.connect() as conn:
        result = await conn.exec_driver_sql("PRAGMA database_list")
        names = {row[1] for row in result.fetchall()}
    assert "logs" in names
