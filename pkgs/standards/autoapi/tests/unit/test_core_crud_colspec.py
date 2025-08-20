from __future__ import annotations

import pytest
from sqlalchemy import Integer, String, create_engine
from sqlalchemy.orm import Mapped, Session as SASession, sessionmaker

from autoapi.v3.bindings.model import bind
from autoapi.v3.core import crud
from autoapi.v3.specs import IO, S, acol
from autoapi.v3.tables import Base


class Thing(Base):
    __tablename__ = "crud_things"
    __allow_unmapped__ = True

    id: Mapped[int] = acol(
        storage=S(type_=Integer, primary_key=True, autoincrement=True),
        io=IO(out_verbs=("read", "list"), filter_ops=("eq",), sortable=True),
    )
    name: Mapped[str] = acol(
        storage=S(type_=String, nullable=False),
        io=IO(
            in_verbs=("create", "update", "replace"),
            out_verbs=("read", "list"),
            filter_ops=("eq",),
            sortable=True,
        ),
    )
    secret: Mapped[str] = acol(
        storage=S(type_=String, nullable=True),
        io=IO(in_verbs=("create", "update"), out_verbs=()),
    )


@pytest.fixture()
def session() -> SASession:
    bind(Thing)
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, future=True)
    with Session() as sess:
        yield sess


@pytest.mark.asyncio
async def test_create(session: SASession) -> None:
    obj = await crud.create(Thing, {"name": "a", "secret": "s"}, session)
    assert obj.id is not None


@pytest.mark.asyncio
async def test_read(session: SASession) -> None:
    obj = await crud.create(Thing, {"name": "a"}, session)
    fetched = await crud.read(Thing, obj.id, session)
    assert fetched.id == obj.id


@pytest.mark.asyncio
async def test_update(session: SASession) -> None:
    obj = await crud.create(Thing, {"name": "a"}, session)
    updated = await crud.update(Thing, obj.id, {"name": "b"}, session)
    assert updated.name == "b"


@pytest.mark.asyncio
async def test_replace(session: SASession) -> None:
    obj = await crud.create(Thing, {"name": "a", "secret": "s"}, session)
    replaced = await crud.replace(Thing, obj.id, {"name": "b"}, session)
    assert replaced.name == "b"
    assert replaced.secret is None


@pytest.mark.asyncio
async def test_delete(session: SASession) -> None:
    obj = await crud.create(Thing, {"name": "a"}, session)
    res = await crud.delete(Thing, obj.id, session)
    assert res == {"deleted": 1}


@pytest.mark.asyncio
async def test_list_filters_and_sort(session: SASession) -> None:
    await crud.create(Thing, {"name": "b"}, session)
    await crud.create(Thing, {"name": "a"}, session)

    res = await crud.list(Thing, {"name": "a"}, db=session)
    assert [r.name for r in res] == ["a"]

    all_items = await crud.list(Thing, {"secret": "s"}, db=session)
    assert {r.name for r in all_items} == {"a", "b"}

    sorted_items = await crud.list(Thing, {}, sort="-name", db=session)
    assert [r.name for r in sorted_items] == ["b", "a"]


@pytest.mark.asyncio
async def test_clear(session: SASession) -> None:
    await crud.create(Thing, {"name": "a"}, session)
    await crud.create(Thing, {"name": "a"}, session)
    await crud.create(Thing, {"name": "b"}, session)

    res = await crud.clear(Thing, {"name": "a"}, db=session)
    assert res == {"deleted": 2}

    remaining = await crud.list(Thing, {}, db=session)
    assert [r.name for r in remaining] == ["b"]
