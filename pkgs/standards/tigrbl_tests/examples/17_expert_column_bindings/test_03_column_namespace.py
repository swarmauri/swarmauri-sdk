from tigrbl.orm.mixins import GUIDPk
from tigrbl.specs import ColumnSpec, F, IO, S, acol
from tigrbl.table import Table
from tigrbl.types import String


def test_column_namespace_exposes_specs():
    class LessonColumnNamespace(Table, GUIDPk):
        __tablename__ = "lesson_column_namespace"
        name = acol(
            storage=S(type_=String, nullable=False),
            field=F(py_type=str),
            io=IO(in_verbs=("create",), out_verbs=("read",)),
        )

    assert isinstance(LessonColumnNamespace.columns.name, ColumnSpec)
