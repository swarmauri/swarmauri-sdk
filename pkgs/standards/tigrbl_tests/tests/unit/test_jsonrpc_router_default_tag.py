from types import SimpleNamespace

from tigrbl.transport import build_jsonrpc_router


def test_jsonrpc_router_default_tag():
    router = SimpleNamespace()
    router = build_jsonrpc_router(router)
    route = router.routes[0]
    assert route.tags == ["rpc"]
