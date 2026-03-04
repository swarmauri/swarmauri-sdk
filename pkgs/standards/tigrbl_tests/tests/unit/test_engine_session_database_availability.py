from sqlalchemy import text

from tigrbl import TableBase, TigrblApp, resolver
from tigrbl.orm.mixins import GUIDPk
from tigrbl.shortcuts.engine import engine, mem
from tigrbl.types import Column, String


class AvailabilityRecord(TableBase, GUIDPk):
    __tablename__ = "availability_records"
    name = Column(String(100), nullable=False)


def test_engine_availability_via_shortcut():
    eng = engine(mem(async_=False))
    sql_engine, session_factory = eng.raw()

    assert sql_engine is not None
    assert callable(session_factory)


def test_session_availability_via_engine_context_manager():
    eng = engine(mem(async_=False))

    with eng.session() as db:
        assert db.execute(text("SELECT 1")).scalar_one() == 1


def test_database_availability_after_app_initialize():
    app = TigrblApp(engine=mem(async_=False))
    app.include_table(AvailabilityRecord)
    app.initialize()

    provider = resolver.resolve_provider(router=app)
    assert provider is not None

    _, session_factory = provider.ensure()

    with session_factory() as db:
        assert db.execute(text("SELECT 1")).scalar_one() == 1
        db.execute(
            text(
                "CREATE TABLE IF NOT EXISTS availability_probe "
                "(id INTEGER PRIMARY KEY, note TEXT)"
            )
        )
        db.commit()
        names = db.execute(
            text("SELECT name FROM sqlite_master WHERE type='table'")
        ).scalars()
        assert "availability_probe" in set(names)
