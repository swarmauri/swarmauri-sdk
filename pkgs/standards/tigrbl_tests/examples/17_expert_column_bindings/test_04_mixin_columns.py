"""Lesson 17: mixin column specs.

Mixins contribute column specs that are merged into the model's column
registry. This keeps shared schema rules centralized in mixins, which is the
preferred design for reusable identifiers like primary keys.
"""

from tigrbl import Base, bind
from tigrbl.orm.mixins import GUIDPk
from tigrbl.specs import F, IO, S, acol
from tigrbl.types import String


def test_column_binding_includes_mixin_specs():
    """Mixin-provided ColumnSpecs appear in the model's column registry."""

    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_column_mixin"
        __allow_unmapped__ = True

        name = acol(
            storage=S(type_=String, nullable=False),
            field=F(py_type=str, constraints={"description": "Display name"}),
            io=IO(in_verbs=("create", "update"), out_verbs=("read", "list")),
        )

    bind(Widget)

    cols = Widget.__tigrbl_cols__
    assert cols["id"].storage.primary_key is True


def test_mixin_column_spec_matches_table_column():
    """Mixin specs should align with the mapped table's primary key column."""

    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_column_mixin_table"
        __allow_unmapped__ = True

        name = acol(
            storage=S(type_=String, nullable=False),
            field=F(py_type=str, constraints={"description": "Display name"}),
            io=IO(in_verbs=("create", "update"), out_verbs=("read", "list")),
        )

    bind(Widget)

    assert set(Widget.__table__.primary_key.columns.keys()) == {"id"}
