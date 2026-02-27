import pytest

from tigrbl import Base, TigrblRouter
from tigrbl.orm.mixins import GUIDPk
from tigrbl.specs import F, IO, S
from tigrbl.shortcuts import acol
from tigrbl.types import Mapped, String


class Widget(Base, GUIDPk):
    __tablename__ = "widgets_router_decl"
    __allow_unmapped__ = True

    name: Mapped[str] = acol(
        storage=S(type_=String, nullable=False),
        field=F(py_type=str),
        io=IO(in_verbs=("create",), out_verbs=("read", "list")),
    )

    __tigrbl_cols__ = {"id": GUIDPk.id, "name": name}


class WidgerRouter(TigrblRouter):
    PREFIX = "/widgets"
    TAGS = ("widgets",)
    TABLES = (Widget,)


@pytest.mark.unit
def test_tigrbl_router_subclass_declares_metadata() -> None:
    class_dir = dir(WidgerRouter)

    assert "TABLES" in class_dir
    assert "TAGS" in class_dir
    assert "PREFIX" in class_dir
    assert WidgerRouter.TABLES == (Widget,)
    assert WidgerRouter.TAGS == ("widgets",)
    assert WidgerRouter.PREFIX == "/widgets"
