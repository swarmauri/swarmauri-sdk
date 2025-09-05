from __future__ import annotations

from ...specs import ColumnSpec, F, S, acol
from ...types import Integer, String, declarative_mixin, Mapped

from .utils import CRUD_IO


@declarative_mixin
class RelationEdge:
    """Marker: row itself is an association—no extra columns required."""

    pass


@declarative_mixin
class MaskableEdge:
    """Edge row with bitmap of verbs/roles."""

    mask: Mapped[int] = acol(
        spec=ColumnSpec(
            storage=S(type_=Integer, nullable=False),
            field=F(py_type=int),
            io=CRUD_IO,
        )
    )


@declarative_mixin
class TaggableEdge:
    tag: Mapped[str] = acol(
        spec=ColumnSpec(
            storage=S(type_=String, nullable=False),
            field=F(py_type=str),
            io=CRUD_IO,
        )
    )


__all__ = ["RelationEdge", "MaskableEdge", "TaggableEdge"]
