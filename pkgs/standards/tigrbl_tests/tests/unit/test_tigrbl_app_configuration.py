import pytest
from fastapi import Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from tigrbl import TigrblApp
from tigrbl.engine.shortcuts import mem


def _auth_dependency(
    credentials: HTTPAuthorizationCredentials = Security(HTTPBearer()),
) -> HTTPAuthorizationCredentials:
    return credentials


@pytest.mark.unit
def test_tigrbl_app_constructor_configuration_sets_metadata() -> None:
    app = TigrblApp(
        engine=mem(async_=False),
        title="Configured App",
        version="2.3.4",
        jsonrpc_prefix="/rpcx",
        system_prefix="/systemx",
    )

    app_dir = dir(app)

    assert "TITLE" in app_dir
    assert "VERSION" in app_dir
    assert "jsonrpc_prefix" in app_dir
    assert "system_prefix" in app_dir
    assert app.TITLE == "Configured App"
    assert app.VERSION == "2.3.4"
    assert app.jsonrpc_prefix == "/rpcx"
    assert app.system_prefix == "/systemx"


@pytest.mark.unit
def test_tigrbl_app_post_instantiation_set_auth_updates_state() -> None:
    app = TigrblApp(engine=mem(async_=False))
    app.set_auth(authn=_auth_dependency, allow_anon=False)

    app_dir = dir(app)

    assert "_authn" in app_dir
    assert "_allow_anon" in app_dir
    assert app._authn is _auth_dependency
    assert app._allow_anon is False
