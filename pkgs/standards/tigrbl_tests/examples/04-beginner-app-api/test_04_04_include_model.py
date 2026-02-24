from __future__ import annotations

import pytest

from tigrbl import TigrblRouter
from tigrbl.engine.shortcuts import mem

from examples.lesson_support import make_widget_model


@pytest.mark.asyncio
async def test_app_includes_model_namespaces() -> None:
<<<<<<< HEAD
    widget = make_widget_model(model_name="WidgetRouter", table_name="widget_router")
    router = TigrblRouter(engine=mem(async_=False))
    router.include_table(widget, prefix="")
    await router.initialize()

    assert "WidgetRouter" in router.models
    assert router.models["WidgetRouter"] is widget
=======
    widget = make_widget_model(model_name="WidgetApi", table_name="widget_api")
    router = TigrblApp(engine=mem(async_=False))
    router.include_model(widget, prefix="")
    await router.initialize()

    assert "WidgetApi" in router.models
    assert router.models["WidgetApi"] is widget
>>>>>>> a8f183f2e9f9d711015dec095ba64838fae67a3c
