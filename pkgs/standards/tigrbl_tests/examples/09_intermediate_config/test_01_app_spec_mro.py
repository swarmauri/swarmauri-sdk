from tigrbl import App
from tigrbl.app.shortcuts import defineAppSpec


def test_app_spec_mro_prefers_subclass():
    """Test app spec mro prefers subclass."""

    # Setup: define a base app spec with defaults.
    class BaseConfig(defineAppSpec(title="Base", jsonrpc_prefix="/rpc")):
        pass

    # Setup: override only the title in a child spec.
    class ChildConfig(defineAppSpec(title="Child"), BaseConfig):
        pass

    # Deployment: instantiate an App that inherits from the child spec.
    class ChildApp(ChildConfig, App):
        pass

    app = ChildApp()
    # Assertion: subclass values take precedence, while base values persist.
    assert app.title == "Child"
    assert app.jsonrpc_prefix == "/rpc"
