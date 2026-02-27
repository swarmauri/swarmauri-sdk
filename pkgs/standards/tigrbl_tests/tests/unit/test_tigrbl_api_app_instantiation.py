import pytest

from tigrbl import Base, TigrblRouter, TigrblApp
from tigrbl.shortcuts.engine import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl import F, IO, S
from tigrbl.shortcuts import acol
from tigrbl.types import Mapped, String


class Theta(Base, GUIDPk):
    __tablename__ = "theta_router_app_inst"
    __allow_unmapped__ = True

    name: Mapped[str] = acol(
        storage=S(type_=String, nullable=False),
        field=F(py_type=str),
        io=IO(in_verbs=("create",), out_verbs=("read", "list")),
    )

    __tigrbl_cols__ = {"id": GUIDPk.id, "name": name}


class ThetaRouter(TigrblRouter):
    TABLES = (Theta,)


@pytest.mark.unit
def test_tigrbl_router_app_instantiation_sets_composed_state() -> None:
    router = ThetaRouter(engine=mem(async_=False))

    class ThetaApp(TigrblApp):
        ROUTERS = (router,)

    app = ThetaApp(engine=mem(async_=False))

    router_dir = dir(router)
    app_dir = dir(app)

    assert "tables" in router_dir
    assert router.tables["Theta"] is Theta
    assert "routers" in app_dir
    assert isinstance(app.routers, dict)
    assert router in app.routers.values()
