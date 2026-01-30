from examples._support import build_simple_api, build_widget_model


def test_jsonrpc_mount_adds_rpc_prefix():
    Widget = build_widget_model("LessonRPC")
    api = build_simple_api(Widget)
    api.mount_jsonrpc(prefix="/rpc")
    route_paths = {route.path for route in api.router.routes}
    assert "/rpc" in route_paths
