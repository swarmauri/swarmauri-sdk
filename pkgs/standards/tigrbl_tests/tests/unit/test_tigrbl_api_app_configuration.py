import pytest
from fastapi import Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from tigrbl import Base, TigrblApi, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.specs import F, IO, S, acol
from tigrbl.types import Mapped, String


def _auth_dependency(
    credentials: HTTPAuthorizationCredentials = Security(HTTPBearer()),
) -> HTTPAuthorizationCredentials:
    return credentials


class Iota(Base, GUIDPk):
    __tablename__ = "iota_api_app_cfg"
    __allow_unmapped__ = True

    name: Mapped[str] = acol(
        storage=S(type_=String, nullable=False),
        field=F(py_type=str),
        io=IO(in_verbs=("create",), out_verbs=("read", "list")),
    )

    __tigrbl_cols__ = {"id": GUIDPk.id, "name": name}


class IotaApi(TigrblApi):
    MODELS = (Iota,)


@pytest.mark.unit
def test_tigrbl_api_app_constructor_configuration_applies_metadata() -> None:
    api = IotaApi(
        engine=mem(async_=False),
        jsonrpc_prefix="/rpcx",
        system_prefix="/systemx",
    )

    class IotaApp(TigrblApp):
        APIS = (api,)

    app = IotaApp(engine=mem(async_=False), title="Iota App", version="9.9.9")

    api_dir = dir(api)
    app_dir = dir(app)

    assert "jsonrpc_prefix" in api_dir
    assert "system_prefix" in api_dir
    assert "TITLE" in app_dir
    assert "VERSION" in app_dir
    assert api.jsonrpc_prefix == "/rpcx"
    assert api.system_prefix == "/systemx"
    assert app.TITLE == "Iota App"
    assert app.VERSION == "9.9.9"
    assert app.apis == [api]


@pytest.mark.unit
def test_tigrbl_api_app_post_instantiation_updates_auth_state() -> None:
    api = IotaApi(engine=mem(async_=False))

    class IotaApp(TigrblApp):
        APIS = (api,)

    app = IotaApp(engine=mem(async_=False))
    api.set_auth(authn=_auth_dependency, allow_anon=False)
    app.set_auth(authn=_auth_dependency, allow_anon=False)

    api_dir = dir(api)
    app_dir = dir(app)

    assert "_authn" in api_dir
    assert "_allow_anon" in api_dir
    assert api._authn is _auth_dependency
    assert api._allow_anon is False
    assert "_authn" in app_dir
    assert "_allow_anon" in app_dir
    assert app._authn is _auth_dependency
    assert app._allow_anon is False
