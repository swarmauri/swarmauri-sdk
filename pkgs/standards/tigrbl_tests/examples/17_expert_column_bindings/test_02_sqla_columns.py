"""Lesson 17: materializing SQLAlchemy columns.

This lesson shows how column specs convert into SQLAlchemy columns that live
on the model's mapped table. The mapping ensures SQLAlchemy metadata is always
aligned with the declarative column specs, which is the preferred pattern for
keeping persistence and schema layers in sync.
"""

from tigrbl import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.specs import F, IO, S, acol
from tigrbl.types import String


def test_column_specs_materialize_sqla_columns():
    """Column specs should produce SQLAlchemy columns on the mapped table."""

    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_column_table"
        __allow_unmapped__ = True

        name = acol(
            storage=S(type_=String, nullable=False),
            field=F(py_type=str, constraints={"description": "Display name"}),
            io=IO(in_verbs=("create", "update"), out_verbs=("read", "list")),
        )

    column_names = set(Widget.__table__.columns.keys())
    assert {"id", "name"}.issubset(column_names)


def test_materialized_columns_preserve_table_name():
    """The model's SQLAlchemy table retains the declared table name."""

    class Widget(Base, GUIDPk):
        __tablename__ = "lessoncolumntablenames"
        __allow_unmapped__ = True

        name = acol(
            storage=S(type_=String, nullable=False),
            field=F(py_type=str, constraints={"description": "Display name"}),
            io=IO(in_verbs=("create", "update"), out_verbs=("read", "list")),
        )

    assert Widget.__table__.name == "lessoncolumntablenames"
