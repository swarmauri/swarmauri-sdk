"""Lesson 17: mixin column specs.

Mixins contribute column specs that are merged into the model's column
registry. This keeps shared schema rules centralized in mixins, which is the
preferred design for reusable identifiers like primary keys.
"""

from tigrbl import bind

from examples._support import build_widget_model


def test_column_binding_includes_mixin_specs():
    """Mixin-provided ColumnSpecs appear in the model's column registry."""
    Widget = build_widget_model("LessonColumnMixin", use_specs=True)

    bind(Widget)

    cols = Widget.__tigrbl_cols__
    assert cols["id"].storage.primary_key is True


def test_mixin_column_spec_matches_table_column():
    """Mixin specs should align with the mapped table's primary key column."""
    Widget = build_widget_model("LessonColumnMixinTable", use_specs=True)

    bind(Widget)

    assert set(Widget.__table__.primary_key.columns.keys()) == {"id"}
