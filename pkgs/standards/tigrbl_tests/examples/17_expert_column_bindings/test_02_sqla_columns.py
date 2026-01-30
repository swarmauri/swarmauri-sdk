"""Lesson 17: materializing SQLAlchemy columns.

This lesson shows how column specs convert into SQLAlchemy columns that live
on the model's mapped table. The mapping ensures SQLAlchemy metadata is always
aligned with the declarative column specs, which is the preferred pattern for
keeping persistence and schema layers in sync.
"""

from examples._support import build_widget_model


def test_column_specs_materialize_sqla_columns():
    """Column specs should produce SQLAlchemy columns on the mapped table."""
    Widget = build_widget_model("LessonColumnTable", use_specs=True)

    column_names = set(Widget.__table__.columns.keys())
    assert {"id", "name"}.issubset(column_names)


def test_materialized_columns_preserve_table_name():
    """The model's SQLAlchemy table retains the declared table name."""
    Widget = build_widget_model("LessonColumnTableName", use_specs=True)

    assert Widget.__table__.name == "lessoncolumntablenames"
