from __future__ import annotations

import inspect

import pytest

from tigrbl import TableBase, TigrblApp
from tigrbl.shortcuts.engine import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


@pytest.mark.asyncio
async def test_rest_create_and_read() -> None:
    class Widget(TableBase, GUIDPk):
        __tablename__ = "lesson_rest_widget"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    app = TigrblApp(engine=mem(async_=False))
    app.include_table(Widget)
    init_result = app.initialize()
    if inspect.isawaitable(init_result):
        await init_result

    paths = {getattr(route, "path", None) for route in app.routes}
    assert "/widget" in paths
    assert "/widget/{item_id}" in paths
