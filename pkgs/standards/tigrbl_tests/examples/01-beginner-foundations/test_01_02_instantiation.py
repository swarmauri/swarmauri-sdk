from __future__ import annotations

from examples.lesson_support import make_widget_model


def test_model_instantiation_assigns_fields() -> None:
    widget = make_widget_model(
        model_name="WidgetInstance", table_name="widget_instance"
    )
    record = widget(name="Starter")
    assert record.name == "Starter"
