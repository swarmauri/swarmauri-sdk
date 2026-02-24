from types import SimpleNamespace

from tigrbl.transport import build_jsonrpc_router


def test_jsonrpc_router_default_tag():
<<<<<<< HEAD
    app = SimpleNamespace()
    router = build_jsonrpc_router(app)
=======
    router = SimpleNamespace()
    router = build_jsonrpc_router(router)
>>>>>>> a8f183f2e9f9d711015dec095ba64838fae67a3c
    route = router.routes[0]
    assert route.tags == ["rpc"]
