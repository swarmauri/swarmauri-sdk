import pytest
from autoapi.v3.autoapp import AutoApp
from autoapi.v3.orm.tables import Base
from autoapi.v3.orm.mixins import GUIDPk
from autoapi.v3.types import Column, String


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


@pytest.mark.asyncio
async def test_dsn_treated_as_base_path(tmp_path):
    """Ensure only schema-attached SQLite database files are created."""
    base = tmp_path / "authn.db"

    class Model(Base, GUIDPk):
        __tablename__ = "things"
        __table_args__ = {"schema": "authn"}
        name = Column(String, nullable=False)

    api = AutoApp(engine=f"sqlite+aiosqlite:///{base}")
    api.include_model(Model)
    await api.initialize()

    attach_path = tmp_path / "authn__authn.db"
    assert attach_path.exists()
    assert not base.exists()
