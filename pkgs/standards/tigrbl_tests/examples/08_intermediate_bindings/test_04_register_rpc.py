from tigrbl import bind, register_rpc
from examples._support import build_widget_model


def test_register_rpc_returns_router():
    """Test register rpc returns router."""
    Widget = build_widget_model("LessonRPCBind")
    specs = bind(Widget)
    register_rpc(Widget, specs)
    assert hasattr(Widget, "rpc")
