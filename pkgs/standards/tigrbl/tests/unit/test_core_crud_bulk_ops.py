import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

from tigrbl.core import crud
from tigrbl.specs import F, IO, S, acol
from tigrbl.types import Integer, Session, String

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
async def test_clear_deletes_matching_rows(session):
    await crud.create(Widget, {"name": "a", "immutable": "x", "value": 1}, session)
    await crud.create(Widget, {"name": "b", "immutable": "y", "value": 2}, session)
    res = await crud.clear(Widget, {"name": "a"}, db=session)
    assert res == {"deleted": 1}
    remaining = await crud.list(Widget, db=session)
    assert [r.name for r in remaining] == ["b"]


@pytest.mark.asyncio
async def test_bulk_create_returns_persisted_items(session):
    items = await crud.bulk_create(
        Widget,
        [
            {"name": "a", "immutable": "x", "value": 1},
            {"name": "b", "immutable": "y", "value": 2},
        ],
        session,
    )
    assert [i.name for i in items] == ["a", "b"]
    rows = await crud.list(Widget, db=session)
    assert len(rows) == 2


@pytest.mark.asyncio
async def test_bulk_update_modifies_rows(session):
    items = await crud.bulk_create(
        Widget,
        [
            {"name": "a", "immutable": "x", "value": 1},
            {"name": "b", "immutable": "y", "value": 2},
        ],
        session,
    )
    updates = [
        {"id": items[0].id, "name": "alpha"},
        {"id": items[1].id, "name": "beta"},
    ]
    updated = await crud.bulk_update(Widget, updates, session)
    assert [u.name for u in updated] == ["alpha", "beta"]
    rows = await crud.list(Widget, db=session)
    assert [r.name for r in rows] == ["alpha", "beta"]


@pytest.mark.asyncio
async def test_bulk_replace_nulls_missing_fields(session):
    [item] = await crud.bulk_create(
        Widget, [{"name": "a", "immutable": "x", "value": 1}], session
    )
    replaced = await crud.bulk_replace(
        Widget, [{"id": item.id, "name": "b", "immutable": "x"}], session
    )
    assert replaced[0].name == "b"
    assert replaced[0].value is None


@pytest.mark.asyncio
async def test_bulk_merge_creates_and_updates(session):
    [item] = await crud.bulk_create(
        Widget, [{"name": "a", "immutable": "x", "value": 1}], session
    )
    rows = [
        {"id": item.id, "name": "alpha"},
        {"name": "b", "immutable": "y", "value": 2},
    ]
    result = await crud.bulk_merge(Widget, rows, session)
    assert {r.name for r in result} == {"alpha", "b"}
    remaining = await crud.list(Widget, db=session)
    assert {r.name for r in remaining} == {"alpha", "b"}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "mode, expected",
    [
        ("none", 0),
        ("one", 1),
        ("all_plus_fake", 2),
    ],
)
async def test_bulk_delete_removes_ids(mode, expected, session):
    items = await crud.bulk_create(
        Widget,
        [
            {"name": "a", "immutable": "x", "value": 1},
            {"name": "b", "immutable": "y", "value": 2},
        ],
        session,
    )
    ids = [i.id for i in items]
    if mode == "none":
        idents = []
    elif mode == "one":
        idents = ids[:1]
    else:
        idents = ids + [999]
    res = await crud.bulk_delete(Widget, idents, session)
    assert res == {"deleted": expected}
    remaining = await crud.list(Widget, db=session)
    assert len(remaining) == len(ids) - expected
