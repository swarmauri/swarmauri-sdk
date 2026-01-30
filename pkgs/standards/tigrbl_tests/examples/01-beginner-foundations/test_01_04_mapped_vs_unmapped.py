from __future__ import annotations

from ..lesson_support import make_widget_model


def test_mapped_and_virtual_columns() -> None:
    widget = make_widget_model(
        model_name="WidgetVirtual",
        table_name="widget_virtual",
        include_virtual=True,
    )
    cols = widget.__tigrbl_cols__
    assert widget.__allow_unmapped__ is True
    assert cols["label"].storage is None
