"""Lesson 17: column specs on models.

This module teaches how column specs live on the model namespace so runtime
code can inspect field metadata without instantiating extra helpers. The
ColumnSpec approach is preferred because it keeps storage, IO, and Python
field rules in a single declarative object per attribute.
"""

from tigrbl import bind
from tigrbl.specs import ColumnSpec

from examples._support import build_widget_model


def test_column_specs_bound_on_model():
    """Column specs should be discoverable on the model's columns registry."""
    Widget = build_widget_model("LessonColumnSpecs", use_specs=True)

    bind(Widget)

    cols = Widget.__tigrbl_cols__
    assert "name" in cols
    assert isinstance(cols["name"], ColumnSpec)


def test_column_specs_expose_field_metadata():
    """Column specs surface field metadata for schema generation workflows."""
    Widget = build_widget_model("LessonColumnSpecsField", use_specs=True)

    bind(Widget)

    field_spec = Widget.__tigrbl_cols__["name"].field
    assert field_spec.py_type is str
