from types import SimpleNamespace

from autoapi.v3.transport import build_jsonrpc_router


def test_jsonrpc_router_default_tag():
    api = SimpleNamespace()
    router = build_jsonrpc_router(api)
    route = router.routes[0]
    assert route.tags == ["system"]
