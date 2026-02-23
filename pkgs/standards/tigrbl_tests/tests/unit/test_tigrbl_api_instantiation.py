import pytest

from tigrbl import Base, TigrblRouter
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.specs import F, IO, S, acol
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


class WidgerRouter(TigrblRouter):
    TABLES = (Widget,)


@pytest.mark.unit
def test_tigrbl_router_instantiation_sets_containers() -> None:
    router = WidgerRouter(engine=mem(async_=False))
    router_dir = dir(router)

    assert "models" in router_dir
    assert "routers" in router_dir
    assert "schemas" in router_dir
    assert "jsonrpc_prefix" in router_dir
    assert "system_prefix" in router_dir
    assert router.models["Widget"] is Widget
