from __future__ import annotations

import pytest

from tigrbl import TigrblApp
from tigrbl.engine.shortcuts import mem

from examples.lesson_support import make_widget_model


@pytest.mark.asyncio
async def test_app_includes_model_namespaces() -> None:
    widget = make_widget_model(model_name="WidgetApi", table_name="widget_api")
    api = TigrblApp(engine=mem(async_=False))
    api.include_model(widget, prefix="")
    await api.initialize()

    assert "WidgetApi" in api.models
    assert api.models["WidgetApi"] is widget
