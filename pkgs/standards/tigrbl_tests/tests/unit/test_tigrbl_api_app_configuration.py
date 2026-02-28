import pytest

from tigrbl import TableBase, TigrblApp, TigrblRouter
from tigrbl.shortcuts.engine import mem
from tigrbl.orm.mixins import GUIDPk
from fastapi.security import HTTPAuthorizationCredentials
from tigrbl import HTTPBearer
from tigrbl.security import Security
from tigrbl._spec import F, IO, S
from tigrbl.shortcuts import acol
from tigrbl.types import Mapped, String


def _auth_dependency(
    credentials: HTTPAuthorizationCredentials = Security(HTTPBearer()),
) -> HTTPAuthorizationCredentials:
    return credentials


class Iota(TableBase, GUIDPk):
    __tablename__ = "iota_router_app_cfg"
    __allow_unmapped__ = True

    name: Mapped[str] = acol(
        storage=S(type_=String, nullable=False),
        field=F(py_type=str),
        io=IO(in_verbs=("create",), out_verbs=("read", "list")),
    )

    __tigrbl_cols__ = {"id": GUIDPk.id, "name": name}


class IotaRouter(TigrblRouter):
    TABLES = (Iota,)


@pytest.mark.unit
def test_tigrbl_router_app_constructor_configuration_applies_metadata() -> None:
    router = IotaRouter(
        engine=mem(async_=False),
        jsonrpc_prefix="/rpcx",
        system_prefix="/systemx",
    )

    class IotaApp(TigrblApp):
        ROUTERS = (router,)

    app = IotaApp(engine=mem(async_=False), title="Iota App", version="9.9.9")

    router_dir = dir(router)
    app_dir = dir(app)

    assert "jsonrpc_prefix" in router_dir
    assert "system_prefix" in router_dir
    assert "TITLE" in app_dir
    assert "VERSION" in app_dir
    assert router.jsonrpc_prefix == "/rpcx"
    assert router.system_prefix == "/systemx"
    assert app.TITLE == "Iota App"
    assert app.VERSION == "9.9.9"
    assert isinstance(app.routers, dict)
    assert router in app.routers.values()


@pytest.mark.unit
def test_tigrbl_router_app_post_instantiation_updates_auth_state() -> None:
    router = IotaRouter(engine=mem(async_=False))

    class IotaApp(TigrblApp):
        ROUTERS = (router,)

    app = IotaApp(engine=mem(async_=False))
    router.set_auth(authn=_auth_dependency, allow_anon=False)
    app.set_auth(authn=_auth_dependency, allow_anon=False)

    router_dir = dir(router)
    app_dir = dir(app)

    assert "_authn" in router_dir
    assert "_allow_anon" in router_dir
    assert router._authn is _auth_dependency
    assert router._allow_anon is False
    assert "_authn" in app_dir
    assert "_allow_anon" in app_dir
    assert app._authn is _auth_dependency
    assert app._allow_anon is False
