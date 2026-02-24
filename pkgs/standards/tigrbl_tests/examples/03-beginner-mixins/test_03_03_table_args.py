from __future__ import annotations

from tigrbl import Base
from tigrbl.types import CheckConstraint, Index, Integer, String, UniqueConstraint
from tigrbl.specs import F, IO, S, acol
from tigrbl.types import Mapped


def test_table_args_constraints() -> None:
    class Entry(Base):
        __tablename__ = "entries"
        __table_args__ = (
            UniqueConstraint("code", name="uq_entries_code"),
            CheckConstraint("value >= 0", name="ck_entries_value"),
            Index("ix_entries_code", "code"),
        )

        id: Mapped[int] = acol(
            storage=S(type_=Integer, primary_key=True, autoincrement=True),
            io=IO(out_verbs=("read", "list")),
        )
        code: Mapped[str] = acol(
            storage=S(type_=String, nullable=False),
            field=F(py_type=str),
            io=IO(in_verbs=("create",), out_verbs=("read", "list")),
        )
        value: Mapped[int] = acol(
            storage=S(type_=Integer, nullable=False),
            field=F(py_type=int),
            io=IO(in_verbs=("create",), out_verbs=("read", "list")),
        )
        __tigrbl_cols__ = {"id": id, "code": code, "value": value}

    constraints = Entry.__table_args__
    assert any(isinstance(item, UniqueConstraint) for item in constraints)
    assert any(isinstance(item, CheckConstraint) for item in constraints)
    assert any(isinstance(item, Index) for item in constraints)
