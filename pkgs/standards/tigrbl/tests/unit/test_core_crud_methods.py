import asyncio
import enum
from typing import Any, Mapping

import pytest
from tigrbl.core import crud
from tigrbl.core.crud import helpers
from tigrbl.engine.shortcuts import engine, mem
from tigrbl.specs import IO, S, F, acol
from tigrbl.types import Column, Integer, SAEnum, SimpleNamespace, String
from sqlalchemy import select
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Widget(Base):
    __tablename__ = "widgets"
    id = acol(
        storage=S(type_=Integer, primary_key=True, autoincrement=True),
        field=F(py_type=int),
        io=IO(out_verbs=("read", "list")),
    )
    name = acol(
        storage=S(type_=String(50)),
        field=F(py_type=str),
        io=IO(
            in_verbs=("create", "update", "replace"),
            out_verbs=("read", "list"),
            mutable_verbs=("create", "update", "replace"),
            filter_ops=("eq", "like", "in", "not_in"),
            sortable=True,
        ),
    )
    value = acol(
        storage=S(type_=Integer, nullable=True),
        field=F(py_type=int),
        io=IO(
            in_verbs=("create", "update", "replace"),
            out_verbs=("read", "list"),
            mutable_verbs=("create", "update", "replace"),
            filter_ops=("eq", "gt", "lt", "gte", "lte"),
            sortable=True,
        ),
    )
    immutable = acol(
        storage=S(type_=String(50)),
        field=F(py_type=str),
        io=IO(
            in_verbs=("create",),
            out_verbs=("read", "list"),
            mutable_verbs=("create",),
        ),
    )


class Status(enum.Enum):
    ONE = "one"
    TWO = "two"


class EnumModel(Base):
    __tablename__ = "enummodel"
    id = Column(Integer, primary_key=True)
    status = Column(SAEnum(Status))


@pytest.fixture()
def session():
    eng = engine(mem(async_=False))
    raw_engine, maker = eng.raw()
    Base.metadata.create_all(raw_engine)
    with maker() as s:
        yield s


class DummyAsync:
    run_sync = True

    def __init__(self):
        self.executed = None
        self.flushed = False
        self.deleted = None

    async def get(self, model, pk):
        return (model, pk)

    async def execute(self, stmt):
        self.executed = stmt
        return "executed"

    async def flush(self):
        self.flushed = True

    async def delete(self, obj):
        self.deleted = obj


def test_is_async_db_detects_async(session):
    assert not helpers._is_async_db(session)
    assert helpers._is_async_db(DummyAsync())


def test_pk_columns(session):
    cols = helpers._pk_columns(Widget)
    assert [c.name for c in cols] == ["id"]

    class NoTable:
        pass

    with pytest.raises(ValueError):
        helpers._pk_columns(NoTable)

    class NoPk:
        __table__ = SimpleNamespace(primary_key=SimpleNamespace(columns=[]))

    with pytest.raises(ValueError):
        helpers._pk_columns(NoPk)


def test_single_pk_name():
    assert helpers._single_pk_name(Widget) == "id"
    col1 = SimpleNamespace(name="a")
    col2 = SimpleNamespace(name="b")

    class TwoPk:
        __table__ = SimpleNamespace(primary_key=SimpleNamespace(columns=[col1, col2]))

    with pytest.raises(NotImplementedError):
        helpers._single_pk_name(TwoPk)


def test_model_columns():
    cols = helpers._model_columns(Widget)
    assert set(cols) == {"id", "name", "value", "immutable"}

    class NoTable:
        pass

    assert helpers._model_columns(NoTable) == ()


def test_colspecs_returns_mapping():
    specs = helpers._colspecs(Widget)
    assert isinstance(specs, Mapping)

    class Dummy:
        __tigrbl_colspecs__ = {"a": 1}

    assert helpers._colspecs(Dummy) == {"a": 1}


def test_filter_in_values_respects_verbs():
    data = {"name": "n", "immutable": "i", "extra": 1}
    create_vals = helpers._filter_in_values(Widget, data, "create")
    assert create_vals == {"name": "n", "immutable": "i", "extra": 1}
    upd_vals = helpers._filter_in_values(Widget, data, "update")
    assert upd_vals == {"name": "n", "extra": 1}


def test_immutable_columns():
    assert helpers._immutable_columns(Widget, "update") == {"immutable"}
    assert helpers._immutable_columns(Widget, "create") == set()


def test_coerce_filters_keeps_valid_ops():
    raw = {
        "name__like": "a%",
        "value__gt": 1,
        "name__bogus": 2,
        "value__>=": 3,
        "unknown": 4,
    }
    coerced = helpers._coerce_filters(Widget, raw)
    assert coerced == {"name__like": "a%", "value__gt": 1, "value__gte": 3}


def test_apply_filters_and_execution(session):
    asyncio.run(
        crud.create(Widget, {"name": "a", "immutable": "x", "value": 1}, session)
    )
    asyncio.run(
        crud.create(Widget, {"name": "b", "immutable": "y", "value": 5}, session)
    )
    clause = helpers._apply_filters(Widget, {"value__gt": 1})
    stmt = select(Widget).where(clause)
    result = asyncio.run(helpers._maybe_execute(session, stmt))
    names = [r.name for r in result.scalars().all()]
    assert names == ["b"]


def test_apply_sort_orders_results(session):
    asyncio.run(
        crud.create(Widget, {"name": "b", "immutable": "x", "value": 2}, session)
    )
    asyncio.run(
        crud.create(Widget, {"name": "a", "immutable": "y", "value": 1}, session)
    )
    exprs = helpers._apply_sort(Widget, "name")
    stmt = select(Widget)
    for e in exprs or []:
        stmt = stmt.order_by(e)
    res = asyncio.run(helpers._maybe_execute(session, stmt))
    assert [r.name for r in res.scalars().all()] == ["a", "b"]
    exprs = helpers._apply_sort(Widget, "-value")
    stmt = select(Widget)
    for e in exprs or []:
        stmt = stmt.order_by(e)
    res = asyncio.run(helpers._maybe_execute(session, stmt))
    assert [r.value for r in res.scalars().all()] == [2, 1]


@pytest.mark.asyncio
async def test_maybe_get_sync(session):
    obj = await crud.create(
        Widget, {"name": "z", "immutable": "x", "value": 9}, session
    )
    fetched = await helpers._maybe_get(session, Widget, obj.id)
    assert fetched.id == obj.id


@pytest.mark.asyncio
async def test_maybe_flush_and_delete_sync(session):
    obj = await crud.create(
        Widget, {"name": "y", "immutable": "x", "value": 3}, session
    )
    await helpers._maybe_flush(session)
    await helpers._maybe_delete(session, obj)
    await helpers._maybe_flush(session)
    assert await helpers._maybe_get(session, Widget, obj.id) is None


@pytest.mark.asyncio
async def test_maybe_wrappers_with_async():
    dummy = DummyAsync()
    await helpers._maybe_get(dummy, Widget, 1)
    await helpers._maybe_execute(dummy, "stmt")
    await helpers._maybe_flush(dummy)
    await helpers._maybe_delete(dummy, object())
    assert dummy.executed == "stmt"
    assert dummy.flushed
    assert dummy.deleted is not None


@pytest.mark.asyncio
async def test_set_attrs_allows_missing():
    obj = Widget(id=1, name="a", value=1, immutable="i")
    helpers._set_attrs(obj, {"name": "b"}, allow_missing=True)
    assert obj.name == "b" and obj.value == 1
    helpers._set_attrs(obj, {"name": "c"}, allow_missing=False)
    assert obj.name == "c" and obj.value is None and obj.immutable is None


def test_validate_enum_values():
    helpers._validate_enum_values(EnumModel, {"status": Status.ONE})
    helpers._validate_enum_values(EnumModel, {"status": "one"})
    helpers._validate_enum_values(EnumModel, {"status": "ONE"})
    with pytest.raises(LookupError):
        helpers._validate_enum_values(EnumModel, {"status": "bad"})


def test_pop_bound_self():
    args = [object(), int]
    helpers._pop_bound_self(args)
    assert args == [int]
    args = [Widget]
    helpers._pop_bound_self(args)
    assert args == [Widget]


def test_extract_db(session):
    args = [session]
    kwargs: dict[str, Any] = {}
    db = helpers._extract_db(args, kwargs)
    assert db is session and args == [] and kwargs == {}
    args = []
    kwargs = {"db": session}
    db = helpers._extract_db(args, kwargs)
    assert db is session and args == [] and kwargs == {}
    with pytest.raises(TypeError):
        helpers._extract_db([], {})


@pytest.mark.parametrize(
    "value,expected",
    [(None, None), (5, 5), (-2, 0), ("7", 7), ("bad", None)],
)
def test_as_pos_int(value, expected):
    assert helpers._as_pos_int(value) == expected


def test_normalize_list_call_variants(session):
    model, params = helpers._normalize_list_call((Widget, {"name": "a"}, session), {})
    assert model is Widget and params["filters"] == {"name": "a"}
    model2, params2 = helpers._normalize_list_call((object(), Widget, session), {})
    assert model2 is Widget and params2["filters"] == {}


@pytest.mark.asyncio
async def test_clear_bulk_and_delete(session):
    await crud.bulk_create(
        Widget,
        [
            {"name": "a", "immutable": "x", "value": 1},
            {"name": "b", "immutable": "y", "value": 2},
        ],
        session,
    )
    res = await crud.clear(Widget, {"name": "a"}, db=session)
    assert res == {"deleted": 1}
    remaining = await crud.list(Widget, db=session)
    assert [r.name for r in remaining] == ["b"]
    objs = await crud.bulk_create(
        Widget,
        [
            {"name": "c", "immutable": "x", "value": 3},
            {"name": "d", "immutable": "y", "value": 4},
        ],
        session,
    )
    updated = await crud.bulk_update(
        Widget,
        [{"id": objs[0].id, "name": "cc"}, {"id": objs[1].id, "value": 40}],
        session,
    )
    assert [u.name for u in updated] == ["cc", "d"]
    replaced = await crud.bulk_replace(
        Widget,
        [{"id": objs[0].id, "name": "ccc"}, {"id": objs[1].id, "name": "ddd"}],
        session,
    )
    assert replaced[0].value is None
    res = await crud.bulk_delete(Widget, [objs[0].id, objs[1].id], session)
    assert res == {"deleted": 2}
    remaining = await crud.list(Widget, db=session)
    assert [r.name for r in remaining] == ["b"]
