import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base

from tigrbl.core import crud
from tigrbl.specs import IO, S, F, acol
from tigrbl.types import Integer, String
from tigrbl.schema import _build_list_params
from sqlalchemy.orm.exc import NoResultFound

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
            filter_ops=("eq", "like", "not_like"),
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


@pytest.fixture()
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        yield s


@pytest.mark.asyncio
async def test_create_respects_in_verbs(session):
    obj = await crud.create(Widget, {"name": "a", "immutable": "one"}, session)
    assert obj.name == "a"
    assert obj.immutable == "one"


@pytest.mark.asyncio
async def test_read_returns_instance(session):
    created = await crud.create(Widget, {"name": "a", "immutable": "one"}, session)
    found = await crud.read(Widget, created.id, session)
    assert found.id == created.id


@pytest.mark.asyncio
async def test_update_skips_immutable(session):
    created = await crud.create(Widget, {"name": "a", "immutable": "one"}, session)
    await crud.update(Widget, created.id, {"name": "b", "immutable": "two"}, session)
    assert created.name == "b"
    assert created.immutable == "one"


@pytest.mark.asyncio
async def test_replace_skips_immutable(session):
    created = await crud.create(Widget, {"name": "a", "immutable": "one"}, session)
    await crud.replace(Widget, created.id, {"name": "c"}, session)
    assert created.name == "c"
    assert created.immutable == "one"


@pytest.mark.asyncio
async def test_delete_removes_row(session):
    created = await crud.create(Widget, {"name": "a", "immutable": "one"}, session)
    await crud.delete(Widget, created.id, session)
    with pytest.raises(NoResultFound):
        await crud.read(Widget, created.id, session)


@pytest.mark.asyncio
async def test_list_applies_allowed_filters_only(session):
    await crud.create(Widget, {"name": "a", "immutable": "x", "value": 1}, session)
    await crud.create(Widget, {"name": "b", "immutable": "y", "value": 2}, session)
    rows = await crud.list(
        Widget,
        filters={"name": "a", "immutable": "nope"},
        db=session,
        skip=0,
        limit=None,
        sort=None,
    )
    assert [r.name for r in rows] == ["a"]


@pytest.mark.asyncio
async def test_list_ignores_non_sortable_columns(session):
    await crud.create(Widget, {"name": "b", "immutable": "x", "value": 2}, session)
    await crud.create(Widget, {"name": "a", "immutable": "y", "value": 1}, session)
    ordered = await crud.list(
        Widget,
        filters=None,
        db=session,
        skip=0,
        limit=None,
        sort="name",
    )
    assert [r.name for r in ordered] == ["a", "b"]
    unsorted = await crud.list(
        Widget,
        filters=None,
        db=session,
        skip=0,
        limit=None,
        sort="immutable",
    )
    assert [r.name for r in unsorted] == ["b", "a"]


@pytest.mark.asyncio
async def test_list_supports_filter_ops_and_desc_sort(session):
    await crud.create(Widget, {"name": "alpha", "immutable": "x", "value": 1}, session)
    await crud.create(Widget, {"name": "bravo", "immutable": "y", "value": 5}, session)
    await crud.create(
        Widget, {"name": "charlie", "immutable": "z", "value": 10}, session
    )

    rows = await crud.list(
        Widget,
        filters={"value__gt": 1, "name__like": "b%"},
        db=session,
        skip=0,
        limit=None,
        sort="-value",
    )
    assert [r.name for r in rows] == ["bravo"]


@pytest.mark.asyncio
async def test_merge_creates_and_updates(session):
    ident = 1
    created = await crud.merge(
        Widget, ident, {"name": "z", "immutable": "lock"}, session
    )
    assert created.name == "z"
    updated = await crud.merge(Widget, ident, {"name": "zz"}, session)
    assert updated.name == "zz"


def test_build_list_params_includes_ops():
    params = _build_list_params(Widget)
    fields = set(params.model_fields.keys())
    assert "sort" in fields
    assert "value__gt" in fields
    assert "name__like" in fields
