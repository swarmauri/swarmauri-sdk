import pytest
from fastapi import Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from tigrbl import TigrblApi
from tigrbl.engine.shortcuts import mem


def _auth_dependency(
    credentials: HTTPAuthorizationCredentials = Security(HTTPBearer()),
) -> HTTPAuthorizationCredentials:
    return credentials


@pytest.mark.unit
def test_tigrbl_api_constructor_configuration_sets_prefixes() -> None:
    def sample_hook() -> None:
        return None

    api = TigrblApi(
        engine=mem(async_=False),
        jsonrpc_prefix="/rpcx",
        system_prefix="/systemx",
        api_hooks={"*": {"pre": [sample_hook]}},
    )

    api_dir = dir(api)

    assert "jsonrpc_prefix" in api_dir
    assert "system_prefix" in api_dir
    assert "_api_hooks_map" in api_dir
    assert api.jsonrpc_prefix == "/rpcx"
    assert api.system_prefix == "/systemx"
    assert api._api_hooks_map == {"*": {"pre": [sample_hook]}}


@pytest.mark.unit
def test_tigrbl_api_post_instantiation_set_auth_updates_state() -> None:
    api = TigrblApi(engine=mem(async_=False))
    api.set_auth(authn=_auth_dependency, allow_anon=False)

    api_dir = dir(api)

    assert "_authn" in api_dir
    assert "_allow_anon" in api_dir
    assert api._authn is _auth_dependency
    assert api._allow_anon is False
