from __future__ import annotations

from tigrbl import bind

from ..lesson_support import make_widget_model


def test_default_opspecs_include_list_and_read() -> None:
    widget = make_widget_model(model_name="WidgetOps", table_name="widget_ops")
    specs = bind(widget)
    aliases = {spec.alias for spec in specs}
    assert "list" in aliases
    assert "read" in aliases
