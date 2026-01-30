from tigrbl import App
from tigrbl.app.shortcuts import defineAppSpec


def test_prefix_precedence_overrides_parent():
    """Test prefix precedence overrides parent."""

    # Setup: define a base system prefix.
    class BaseConfig(defineAppSpec(system_prefix="/system")):
        pass

    # Setup: override the prefix in the child spec.
    class ChildConfig(defineAppSpec(system_prefix="/systemz"), BaseConfig):
        pass

    # Deployment: instantiate the App from the child spec.
    class ChildApp(ChildConfig, App):
        pass

    app = ChildApp()
    # Assertion: child prefixes override base config.
    assert app.system_prefix == "/systemz"
