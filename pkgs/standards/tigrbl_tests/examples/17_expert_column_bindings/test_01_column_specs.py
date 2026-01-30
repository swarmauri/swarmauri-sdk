from tigrbl import bind
from tigrbl.specs import ColumnSpec

from examples._support import build_widget_model


def test_column_specs_bound_on_model():
    Widget = build_widget_model("LessonColumnSpecs", use_specs=True)

    bind(Widget)

    cols = Widget.__tigrbl_cols__
    assert "name" in cols
    assert isinstance(cols["name"], ColumnSpec)
