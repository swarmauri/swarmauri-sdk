from __future__ import annotations

import pytest

from tigrbl import TigrblApp
from tigrbl.engine.shortcuts import engine as build_engine, mem
from tigrbl.specs import F, IO, S, acol
from tigrbl.table import Base
from tigrbl.types import Integer, String


@pytest.mark.asyncio
async def test_list_core_respects_nested_filter_payloads():
    class Thing(Base):
        __tablename__ = "list_filter_things"

        id = acol(
            storage=S(type_=Integer, primary_key=True, autoincrement=True),
            field=F(py_type=int),
            io=IO(in_verbs=("create",), out_verbs=("read", "list")),
        )
        name = acol(
            storage=S(type_=String(40), nullable=False),
            field=F(py_type=str),
            io=IO(
                in_verbs=("create",),
                out_verbs=("read", "list"),
                filter_ops=("eq", "ilike"),
            ),
        )

    cfg = mem()
    app = TigrblApp(engine=build_engine(cfg))
    app.include_model(Thing)
    await app.initialize()

    async with app.engine.asession() as session:
        await Thing.handlers.create.core({"db": session, "payload": {"name": "alpha"}})
        await Thing.handlers.create.core({"db": session, "payload": {"name": "bravo"}})

        rows = await Thing.handlers.list.core(
            {"db": session, "payload": {"filters": {"name": "bravo"}}}
        )
        assert [row.name for row in rows] == ["bravo"]

        rows = await Thing.handlers.list.core(
            {"db": session, "payload": {"filters": {"name__ilike": "%a%"}}}
        )
        assert sorted(row.name for row in rows) == ["alpha", "bravo"]
