from __future__ import annotations

import pytest

from tigrbl import TigrblApp
from tigrbl.engine.shortcuts import mem

from examples.lesson_support import make_widget_model


@pytest.mark.asyncio
async def test_rest_router_is_attached() -> None:
    widget = make_widget_model(model_name="WidgetRouter", table_name="widget_router")
<<<<<<< HEAD
    app = TigrblApp(engine=mem(async_=False))
    app.include_table(widget, prefix="")
    await app.initialize()

    assert app.routers["WidgetRouter"] is widget.rest.router
=======
    router = TigrblApp(engine=mem(async_=False))
    router.include_model(widget, prefix="")
    await router.initialize()

    assert router.routers["WidgetRouter"] is widget.rest.router
>>>>>>> a8f183f2e9f9d711015dec095ba64838fae67a3c
