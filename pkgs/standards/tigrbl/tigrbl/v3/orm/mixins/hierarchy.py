from __future__ import annotations

from ...specs import ColumnSpec, F, S, acol
from ...specs.storage_spec import ForeignKeySpec
from ...types import PgUUID, UUID, String, declarative_mixin, declared_attr, Mapped

from .utils import CRUD_IO


@declarative_mixin
class Contained:
    @declared_attr
    def parent_id(cls) -> Mapped[UUID]:
        if not hasattr(cls, "parent_table"):
            raise AttributeError("subclass must set parent_table")
        spec = ColumnSpec(
            storage=S(
                type_=PgUUID(as_uuid=True),
                fk=ForeignKeySpec(target=f"{cls.parent_table}.id"),
                nullable=False,
            ),
            field=F(py_type=UUID),
            io=CRUD_IO,
        )
        return acol(spec=spec)


@declarative_mixin
class TreeNode:
    """Self-nesting hierarchy."""

    @declared_attr
    def parent_id(cls) -> Mapped[UUID | None]:
        spec = ColumnSpec(
            storage=S(
                type_=PgUUID(as_uuid=True),
                fk=ForeignKeySpec(target=f"{cls.__tablename__}.id"),
                nullable=True,
            ),
            field=F(py_type=UUID),
            io=CRUD_IO,
        )
        return acol(spec=spec)

    path: Mapped[str] = acol(
        spec=ColumnSpec(
            storage=S(type_=String),
            field=F(py_type=str),
            io=CRUD_IO,
        )
    )


__all__ = ["Contained", "TreeNode"]
