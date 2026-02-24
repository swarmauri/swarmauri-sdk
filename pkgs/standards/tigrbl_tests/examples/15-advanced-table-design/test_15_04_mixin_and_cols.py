from __future__ import annotations

from tigrbl import Base
from tigrbl.orm.mixins import ActiveToggle
from tigrbl.specs import F, IO, S, acol
from tigrbl.types import Integer, Mapped, String


def test_mixin_and_custom_columns() -> None:
    class Feature(Base, ActiveToggle):
        __tablename__ = "features"

        id: Mapped[int] = acol(
            storage=S(type_=Integer, primary_key=True, autoincrement=True),
            io=IO(out_verbs=("read", "list")),
        )
        name: Mapped[str] = acol(
            storage=S(type_=String, nullable=False),
            field=F(py_type=str),
            io=IO(in_verbs=("create",), out_verbs=("read", "list")),
        )
        __tigrbl_cols__ = {"id": id, "name": name, "is_active": ActiveToggle.is_active}

    assert Feature.is_active.storage is not None
    assert "is_active" in Feature.__tigrbl_cols__
