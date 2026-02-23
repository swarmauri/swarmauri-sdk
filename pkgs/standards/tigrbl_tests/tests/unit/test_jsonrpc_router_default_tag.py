from types import SimpleNamespace

from tigrbl.transport import build_jsonrpc_router


def test_jsonrpc_router_default_tag():
    app = SimpleNamespace()
    router = build_jsonrpc_router(app)
    route = router.routes[0]
    assert route.tags == ["rpc"]
