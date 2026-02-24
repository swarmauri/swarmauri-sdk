from __future__ import annotations

import warnings

from sqlalchemy import Integer, String
from sqlalchemy.exc import SAWarning

from tigrbl.column import ColumnSpec, S
from tigrbl.table._base import Base


def test_columnspec_inheritance_does_not_warn() -> None:
    class Parent(Base):
        __tablename__ = "test_parent"
        __mapper_args__ = {
            "polymorphic_identity": "parent",
            "polymorphic_on": "kind",
        }
        id: int = ColumnSpec(storage=S(type_=Integer, primary_key=True))
        kind: str = ColumnSpec(storage=S(type_=String))

    with warnings.catch_warnings():
        warnings.simplefilter("error", SAWarning)

        class Child(Parent):
            __mapper_args__ = {"polymorphic_identity": "child"}

            # no extra columns, we just inherit Parent.id
            pass
