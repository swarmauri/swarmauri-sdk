import pytest
from sqlalchemy import Integer, String, create_engine, select
from sqlalchemy.orm import sessionmaker

from autoapi.v3.bindings import handlers
from autoapi.v3.tables._base import Base
from autoapi.v3.specs.shortcuts import acol, F, IO, S


class Item(Base):
    id = acol(
        storage=S(type_=Integer, primary_key=True),
        field=F(py_type=int),
        io=IO(alias_in="item_id"),
    )
    name = acol(
        storage=S(type_=String),
        field=F(py_type=str),
        io=IO(alias_in="n", filter_ops=("list", "clear")),
    )


def _session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


@pytest.mark.asyncio
async def test_delete_uses_pk_alias():
    db = _session()
    db.add(Item(id=1, name="a"))
    db.commit()

    step = handlers._wrap_core(Item, "delete")
    ctx = {"path_params": {"item_id": "1"}, "db": db}
    result = await step(ctx)
    assert result == {"id": 1}
    assert db.get(Item, 1) is None


@pytest.mark.asyncio
async def test_clear_respects_filters_with_alias():
    db = _session()
    db.add_all([Item(id=1, name="a"), Item(id=2, name="b")])
    db.commit()

    step = handlers._wrap_core(Item, "clear")
    ctx = {"payload": {"n": "b"}, "db": db}
    result = await step(ctx)
    assert result == {"deleted": 1}
    remaining = db.execute(select(Item)).scalars().all()
    assert [r.name for r in remaining] == ["a"]
