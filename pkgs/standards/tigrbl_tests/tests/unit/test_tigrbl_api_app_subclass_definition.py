import pytest

from tigrbl import Base, TigrblRouter, TigrblApp
from tigrbl.orm.mixins import GUIDPk
from tigrbl._spec import FieldSpec as F, IOSpec as IO, StorageSpec as S
from tigrbl.shortcuts import acol
from tigrbl.types import Mapped, String


class Zeta(Base, GUIDPk):
    __tablename__ = "zeta_router_app_decl"
    __allow_unmapped__ = True

    name: Mapped[str] = acol(
        storage=S(type_=String, nullable=False),
        field=F(py_type=str),
        io=IO(in_verbs=("create",), out_verbs=("read", "list")),
    )

    __tigrbl_cols__ = {"id": GUIDPk.id, "name": name}


class ZetaRouter(TigrblRouter):
    TABLES = (Zeta,)


class ZetaApp(TigrblApp):
    ROUTERS = (ZetaRouter,)


@pytest.mark.unit
def test_tigrbl_router_app_subclass_declares_composition() -> None:
    router_dir = dir(ZetaRouter)
    app_dir = dir(ZetaApp)

    assert "TABLES" in router_dir
    assert "ROUTERS" in app_dir
    assert ZetaRouter.TABLES == (Zeta,)
    assert ZetaApp.ROUTERS == (ZetaRouter,)
