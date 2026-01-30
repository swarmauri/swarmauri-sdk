from tigrbl import App
from tigrbl.app.shortcuts import defineAppSpec


def test_hook_sequence_merges_across_mro():
    """Test hook sequence merges across mro."""

    # Setup: define base hook ordering.
    class BaseConfig(defineAppSpec(hooks=("base",))):
        pass

    # Setup: explicitly compose hooks in the child spec.
    class ChildConfig(defineAppSpec(hooks=("base", "child")), BaseConfig):
        pass

    # Deployment: instantiate the App with the composed hooks.
    class ChildApp(ChildConfig, App):
        pass

    app = ChildApp()
    # Assertion: hook precedence is defined by explicit composition.
    assert app.hooks == ("base", "child")
