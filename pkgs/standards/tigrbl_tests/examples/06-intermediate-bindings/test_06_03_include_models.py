from __future__ import annotations

import pytest

from tigrbl import TigrblApp
from tigrbl.engine.shortcuts import mem

from examples.lesson_support import make_widget_model


@pytest.mark.asyncio
async def test_include_models_registers_resources() -> None:
    widget = make_widget_model(model_name="WidgetA", table_name="widget_a")
    gadget = make_widget_model(model_name="WidgetB", table_name="widget_b")

    router = TigrblApp(engine=mem(async_=False))
    router.include_models([widget, gadget], base_prefix="")
    await router.initialize()

    assert "WidgetA" in router.models
    assert "WidgetB" in router.models
