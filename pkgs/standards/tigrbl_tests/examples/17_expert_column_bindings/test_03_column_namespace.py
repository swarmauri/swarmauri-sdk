"""Lesson 17: column namespace access.

Column specs are accessible via the model's ``columns`` namespace, which makes
it easy to discover field metadata without scanning class attributes directly.
This pattern is preferred because it centralizes spec access and encourages
consistent introspection across models.
"""

from tigrbl.orm.mixins import GUIDPk
from tigrbl.specs import ColumnSpec, F, IO, S, acol
from tigrbl.table import Table
from tigrbl.types import String


def test_column_namespace_exposes_specs():
    """The ``columns`` namespace exposes ColumnSpec instances by attribute."""

    class LessonColumnNamespace(Table, GUIDPk):
        __tablename__ = "lesson_column_namespace"
        name = acol(
            storage=S(type_=String, nullable=False),
            field=F(py_type=str),
            io=IO(in_verbs=("create",), out_verbs=("read",)),
        )

    assert isinstance(LessonColumnNamespace.columns.name, ColumnSpec)


def test_column_namespace_includes_field_and_storage():
    """ColumnSpec objects hold storage and field metadata for each column."""

    class LessonColumnNamespaceMeta(Table, GUIDPk):
        __tablename__ = "lesson_column_namespace_meta"
        name = acol(
            storage=S(type_=String, nullable=False),
            field=F(py_type=str),
            io=IO(in_verbs=("create",), out_verbs=("read",)),
        )

    spec = LessonColumnNamespaceMeta.columns.name
    assert spec.field.py_type is str
    assert spec.storage.nullable is False
