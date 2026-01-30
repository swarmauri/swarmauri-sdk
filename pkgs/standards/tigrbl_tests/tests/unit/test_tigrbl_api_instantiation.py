import pytest

from tigrbl import Base, TigrblApi
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.specs import F, IO, S, acol
from tigrbl.types import Mapped, String


class Widget(Base, GUIDPk):
    __tablename__ = "widgets_api_inst"
    __allow_unmapped__ = True

    name: Mapped[str] = acol(
        storage=S(type_=String, nullable=False),
        field=F(py_type=str),
        io=IO(in_verbs=("create",), out_verbs=("read", "list")),
    )

    __tigrbl_cols__ = {"id": GUIDPk.id, "name": name}


class WidgetApi(TigrblApi):
    MODELS = (Widget,)


@pytest.mark.unit
def test_tigrbl_api_instantiation_sets_containers() -> None:
    api = WidgetApi(engine=mem(async_=False))
    api_dir = dir(api)

    assert "models" in api_dir
    assert "routers" in api_dir
    assert "schemas" in api_dir
    assert "jsonrpc_prefix" in api_dir
    assert "system_prefix" in api_dir
    assert api.models["Widget"] is Widget
