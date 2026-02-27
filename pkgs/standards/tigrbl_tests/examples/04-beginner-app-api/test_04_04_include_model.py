from __future__ import annotations

import pytest

from tigrbl import TigrblRouter
from tigrbl.engine.shortcuts import mem

from tigrbl_tests.examples.lesson_support import make_widget_model


@pytest.mark.asyncio
async def test_app_includes_model_namespaces() -> None:
    widget = make_widget_model(model_name="WidgetRouter", table_name="widget_router")
    router = TigrblRouter(engine=mem(async_=False))
    router.include_table(widget, prefix="")
    await router.initialize()

    assert "WidgetRouter" in router.tables
    assert router.tables["WidgetRouter"] is widget
