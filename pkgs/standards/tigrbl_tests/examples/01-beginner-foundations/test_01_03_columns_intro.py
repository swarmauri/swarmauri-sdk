from __future__ import annotations

from tigrbl.types import Integer, String

from ..lesson_support import make_widget_model


def test_columns_are_registered_on_model() -> None:
    widget = make_widget_model(model_name="WidgetCols", table_name="widget_cols")
    cols = widget.__tigrbl_cols__
    assert set(cols.keys()) == {"id", "name"}
    assert cols["id"].storage.type_ is Integer
    assert cols["name"].storage.type_ is String
