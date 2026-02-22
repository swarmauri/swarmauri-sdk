from __future__ import annotations

import pytest

from tigrbl import TigrblApp
from tigrbl.engine.shortcuts import mem

from examples.lesson_support import make_widget_model


@pytest.mark.asyncio
async def test_app_includes_model_namespaces() -> None:
    widget = make_widget_model(model_name="WidgetApi", table_name="widget_api")
    router = TigrblApp(engine=mem(async_=False))
    router.include_model(widget, prefix="")
    await router.initialize()

    assert "WidgetApi" in router.models
    assert router.models["WidgetApi"] is widget
