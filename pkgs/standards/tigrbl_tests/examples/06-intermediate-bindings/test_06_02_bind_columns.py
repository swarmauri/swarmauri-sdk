from __future__ import annotations

from tigrbl import bind

from ..lesson_support import make_widget_model


def test_bind_exposes_columns_namespace() -> None:
    widget = make_widget_model(model_name="WidgetColumns", table_name="widget_columns")
    bind(widget)
    assert "id" in widget.__tigrbl_cols__
    assert "name" in widget.__tigrbl_cols__
