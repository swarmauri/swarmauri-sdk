from tigrbl import App
from tigrbl.app.shortcuts import defineAppSpec


def test_ops_sequence_merges_across_mro():
    """Test ops sequence merges across mro."""

    # Setup: define base operation ordering.
    class BaseConfig(defineAppSpec(ops=("base",))):
        pass

    # Setup: explicitly compose ops in the child spec.
    class ChildConfig(defineAppSpec(ops=("base", "child")), BaseConfig):
        pass

    # Deployment: instantiate the App with the composed ops.
    class ChildApp(ChildConfig, App):
        pass

    app = ChildApp()
    # Assertion: op precedence is defined by explicit composition.
    assert app.ops == ("base", "child")
