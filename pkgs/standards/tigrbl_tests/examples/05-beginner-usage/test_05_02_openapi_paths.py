from __future__ import annotations

import inspect

import pytest

from tigrbl import TableBase, TigrblApp
from tigrbl.shortcuts.engine import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import String
from tigrbl.column import F, IO, S, acol


@pytest.mark.asyncio
async def test_openapi_includes_widget_paths() -> None:
    class Widget(TableBase, GUIDPk):
        __tablename__ = "lesson_openapi_widget"
        __allow_unmapped__ = True

        name = acol(
            storage=S(type_=String, nullable=False),
            field=F(py_type=str),
            io=IO(in_verbs=("create",), out_verbs=("read", "list")),
        )

    app = TigrblApp(engine=mem(async_=False))
    app.include_table(Widget)
    init_result = app.initialize()
    if inspect.isawaitable(init_result):
        await init_result

    paths = app.openapi()["paths"]
    assert "/widget" in paths
    assert "/widget/{item_id}" in paths
