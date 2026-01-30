from __future__ import annotations

import pytest

from tigrbl import TigrblApp
from tigrbl.engine.shortcuts import mem

from examples.lesson_support import make_widget_model


@pytest.mark.asyncio
async def test_rest_router_is_attached() -> None:
    widget = make_widget_model(model_name="WidgetRouter", table_name="widget_router")
    api = TigrblApp(engine=mem(async_=False))
    api.include_model(widget, prefix="")
    await api.initialize()

    assert api.routers["WidgetRouter"] is widget.rest.router
