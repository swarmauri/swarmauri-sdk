import pytest

from tigrbl import Base, TigrblRouter
from tigrbl.shortcuts.engine import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl._spec import F, IO, S
from tigrbl.shortcuts import acol
from tigrbl.types import Mapped, String


class Widget(Base, GUIDPk):
    __tablename__ = "widgets_router_inst"
    __allow_unmapped__ = True

    name: Mapped[str] = acol(
        storage=S(type_=String, nullable=False),
        field=F(py_type=str),
        io=IO(in_verbs=("create",), out_verbs=("read", "list")),
    )

    __tigrbl_cols__ = {"id": GUIDPk.id, "name": name}


class WidgetRouter(TigrblRouter):
    TABLES = (Widget,)


@pytest.mark.unit
def test_tigrbl_router_instantiation_sets_containers() -> None:
    router = WidgetRouter(engine=mem(async_=False))
    router_dir = dir(router)

    assert "tables" in router_dir
    assert "routers" in router_dir
    assert "schemas" in router_dir
    assert "jsonrpc_prefix" in router_dir
    assert "system_prefix" in router_dir
    assert router.tables["Widget"] is Widget
