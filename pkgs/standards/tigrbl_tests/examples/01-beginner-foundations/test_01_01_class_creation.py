from __future__ import annotations

from tigrbl import TableBase
from tigrbl_tests.examples.lesson_support import make_widget_model


def test_class_creation_basics() -> None:
    widget = make_widget_model(
        model_name="WidgetIntro",
        table_name="widget_intro",
        resource="widget_intro",
    )
    assert issubclass(widget, TableBase)
    assert widget.__tablename__ == "widget_intro"
    assert widget.__resource__ == "widget_intro"
