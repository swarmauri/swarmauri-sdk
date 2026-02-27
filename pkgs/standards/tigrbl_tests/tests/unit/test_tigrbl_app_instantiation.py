import pytest

from tigrbl import Base, TigrblApp
from tigrbl.shortcuts.engine import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl._spec import F, IO, S
from tigrbl.shortcuts import acol
from tigrbl.types import Mapped, String


class Widget(Base, GUIDPk):
    __tablename__ = "widgets_app_inst"
    __allow_unmapped__ = True

    name: Mapped[str] = acol(
        storage=S(type_=String, nullable=False),
        field=F(py_type=str),
        io=IO(in_verbs=("create",), out_verbs=("read", "list")),
    )

    __tigrbl_cols__ = {"id": GUIDPk.id, "name": name}


class WidgetApp(TigrblApp):
    TABLES = (Widget,)


@pytest.mark.unit
def test_tigrbl_app_instantiation_sets_containers() -> None:
    app = WidgetApp(engine=mem(async_=False))
    app_dir = dir(app)

    assert "tables" in app_dir
    assert "routers" in app_dir
    assert "schemas" in app_dir
    assert "jsonrpc_prefix" in app_dir
    assert "system_prefix" in app_dir
    assert app.tables["Widget"] is Widget
