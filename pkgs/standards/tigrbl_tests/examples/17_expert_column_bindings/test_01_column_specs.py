"""Lesson 17: column specs on models.

This module teaches how column specs live on the model namespace so runtime
code can inspect field metadata without instantiating extra helpers. The
ColumnSpec approach is preferred because it keeps storage, IO, and Python
field rules in a single declarative object per attribute.
"""

from tigrbl import Base, bind
from tigrbl.orm.mixins import GUIDPk
from tigrbl.specs import ColumnSpec, F, IO, S, acol
from tigrbl.types import String


def test_column_specs_bound_on_model():
    """Column specs should be discoverable on the model's columns registry."""

    class LessonColumnSpecs(Base, GUIDPk):
        __tablename__ = "lessoncolumnspecss"
        __allow_unmapped__ = True

        name = acol(
            storage=S(type_=String, nullable=False),
            field=F(py_type=str, constraints={"description": "Display name"}),
            io=IO(in_verbs=("create", "update"), out_verbs=("read", "list")),
        )

    Widget = LessonColumnSpecs

    bind(Widget)

    cols = Widget.__tigrbl_cols__
    assert "name" in cols
    assert isinstance(cols["name"], ColumnSpec)


def test_column_specs_expose_field_metadata():
    """Column specs surface field metadata for schema generation workflows."""

    class LessonColumnSpecsField(Base, GUIDPk):
        __tablename__ = "lessoncolumnspecsfields"
        __allow_unmapped__ = True

        name = acol(
            storage=S(type_=String, nullable=False),
            field=F(py_type=str, constraints={"description": "Display name"}),
            io=IO(in_verbs=("create", "update"), out_verbs=("read", "list")),
        )

    Widget = LessonColumnSpecsField

    bind(Widget)

    field_spec = Widget.__tigrbl_cols__["name"].field
    assert field_spec.py_type is str
