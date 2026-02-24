from __future__ import annotations

from tigrbl import bind

from examples.lesson_support import make_widget_model


def test_bind_builds_opspecs() -> None:
    widget = make_widget_model(model_name="WidgetBind", table_name="widget_bind")
    specs = bind(widget)
    assert any(spec.alias == "create" for spec in specs)
    assert hasattr(widget, "opspecs")
