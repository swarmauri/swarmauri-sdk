import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base

from autoapi.v3.core import crud
from autoapi.v3.columns import acol as col
from autoapi.v3.specs import acol as spec_acol, IO, S, F
from autoapi.v3.types import Integer, String
from sqlalchemy.orm.exc import NoResultFound

Base = declarative_base()


class Widget(Base):
    __tablename__ = "widgets"
    id = col(
        spec=spec_acol(
            storage=S(type_=Integer, primary_key=True),
            field=F(py_type=int),
            io=IO(out_verbs=("read", "list")),
        )
    )
    name = col(
        spec=spec_acol(
            storage=S(type_=String(50)),
            field=F(py_type=str),
            io=IO(
                in_verbs=("create", "update", "replace"),
                out_verbs=("read", "list"),
                mutable_verbs=("create", "update", "replace"),
                filter_ops=("eq",),
                sortable=True,
            ),
        )
    )
    immutable = col(
        spec=spec_acol(
            storage=S(type_=String(50)),
            field=F(py_type=str),
            io=IO(
                in_verbs=("create",),
                out_verbs=("read", "list"),
                mutable_verbs=("create",),
            ),
        )
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
    await crud.create(Widget, {"name": "a", "immutable": "x"}, session)
    await crud.create(Widget, {"name": "b", "immutable": "y"}, session)
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
    await crud.create(Widget, {"name": "b", "immutable": "x"}, session)
    await crud.create(Widget, {"name": "a", "immutable": "y"}, session)
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
async def test_list_supports_descending_sort(session):
    await crud.create(Widget, {"name": "a", "immutable": "x"}, session)
    await crud.create(Widget, {"name": "b", "immutable": "y"}, session)
    rows = await crud.list(
        Widget,
        filters=None,
        db=session,
        skip=0,
        limit=None,
        sort="name:desc",
    )
    assert [r.name for r in rows] == ["b", "a"]
