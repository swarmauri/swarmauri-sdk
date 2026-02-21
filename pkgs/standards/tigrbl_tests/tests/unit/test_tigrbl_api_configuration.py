import pytest

from tigrbl import TigrblRouter
from tigrbl.security import HTTPAuthorizationCredentials, HTTPBearer
from tigrbl.types import Security
from tigrbl.engine.shortcuts import mem


def _auth_dependency(
    credentials: HTTPAuthorizationCredentials = Security(HTTPBearer()),
) -> HTTPAuthorizationCredentials:
    return credentials


@pytest.mark.unit
def test_tigrbl_api_constructor_configuration_sets_prefixes() -> None:
    def sample_hook() -> None:
        return None

    router = TigrblRouter(
        engine=mem(async_=False),
        jsonrpc_prefix="/rpcx",
        system_prefix="/systemx",
        router_hooks={"*": {"pre": [sample_hook]}},
    )

    router_dir = dir(router)

    assert "jsonrpc_prefix" in router_dir
    assert "system_prefix" in router_dir
    assert "_router_hooks_map" in router_dir
    assert router.jsonrpc_prefix == "/rpcx"
    assert router.system_prefix == "/systemx"
    assert router._router_hooks_map == {"*": {"pre": [sample_hook]}}


@pytest.mark.unit
def test_tigrbl_api_post_instantiation_set_auth_updates_state() -> None:
    router = TigrblRouter(engine=mem(async_=False))
    router.set_auth(authn=_auth_dependency, allow_anon=False)

    router_dir = dir(router)

    assert "_authn" in router_dir
    assert "_allow_anon" in router_dir
    assert router._authn is _auth_dependency
    assert router._allow_anon is False


@pytest.mark.unit
def test_tigrbl_api_class_prefix_defaults() -> None:
    assert TigrblRouter.REST_PREFIX == "/api"
    assert TigrblRouter.RPC_PREFIX == "/rpc"
    assert TigrblRouter.SYSTEM_PREFIX == "/system"

    router = TigrblRouter(engine=mem(async_=False))
    assert router.rest_prefix == "/api"
    assert router.rpc_prefix == "/rpc"
    assert router.system_prefix == "/system"
