import pytest
from sqlalchemy import Integer, String, select
from sqlalchemy.orm import Mapped

from autoapi.v3 import Base
from autoapi.v3.specs import F, IO, S, acol


def test_pg_sync_db_session(pg_db_session):
    engine, get_db = pg_db_session

    class Widget(Base):
        __tablename__ = "widgets_sync"
        id: Mapped[int] = acol(
            storage=S(type_=Integer, primary_key=True, autoincrement=True)
        )
        name: Mapped[str] = acol(
            storage=S(type_=String, nullable=False),
            field=F(),
            io=IO(in_verbs=("create",), out_verbs=("read", "list")),
        )
        __autoapi_cols__ = {"id": id, "name": name}

    Base.metadata.create_all(bind=engine)

    with get_db() as db:
        db.add(Widget(name="alpha"))
        db.commit()

    with get_db() as db:
        assert db.query(Widget).count() == 1


@pytest.mark.asyncio
async def test_pg_async_db_session(async_pg_db_session):
    engine, get_db = async_pg_db_session

    class Widget(Base):
        __tablename__ = "widgets_async"
        id: Mapped[int] = acol(
            storage=S(type_=Integer, primary_key=True, autoincrement=True)
        )
        name: Mapped[str] = acol(
            storage=S(type_=String, nullable=False),
            field=F(),
            io=IO(in_verbs=("create",), out_verbs=("read", "list")),
        )
        __autoapi_cols__ = {"id": id, "name": name}

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with get_db() as db:
        db.add(Widget(name="beta"))
        await db.commit()

    async with get_db() as db:
        result = await db.execute(select(Widget))
        items = result.scalars().all()
        assert len(items) == 1
