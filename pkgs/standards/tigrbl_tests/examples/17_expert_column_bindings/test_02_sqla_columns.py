from examples._support import build_widget_model


def test_column_specs_materialize_sqla_columns():
    Widget = build_widget_model("LessonColumnTable", use_specs=True)

    column_names = set(Widget.__table__.columns.keys())
    assert {"id", "name"}.issubset(column_names)
