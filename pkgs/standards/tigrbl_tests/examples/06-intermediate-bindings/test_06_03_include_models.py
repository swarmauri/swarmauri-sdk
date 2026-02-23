from __future__ import annotations

import pytest

from tigrbl import TigrblApp
from tigrbl.engine.shortcuts import mem

from examples.lesson_support import make_widget_model


@pytest.mark.asyncio
async def test_include_models_registers_resources() -> None:
    widget = make_widget_model(model_name="WidgetA", table_name="widget_a")
    gadget = make_widget_model(model_name="WidgetB", table_name="widget_b")

    app = TigrblApp(engine=mem(async_=False))
    app.include_tables([widget, gadget], base_prefix="")
    await app.initialize()

    assert "WidgetA" in app.models
    assert "WidgetB" in app.models
