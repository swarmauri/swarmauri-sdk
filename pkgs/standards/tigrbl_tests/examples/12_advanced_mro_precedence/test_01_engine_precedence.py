from tigrbl import App
from tigrbl.app.shortcuts import defineAppSpec
from tigrbl.engine.shortcuts import mem


def test_engine_precedence_resolves_latest():
    """Test engine precedence resolves latest."""

    # Setup: define distinct engine configs to demonstrate precedence.
    base_engine = mem(async_=False)
    child_engine = mem(async_=False)

    class BaseConfig(defineAppSpec(engine=base_engine)):
        pass

    # Setup: override the engine in the child spec.
    class ChildConfig(defineAppSpec(engine=child_engine), BaseConfig):
        pass

    # Deployment: instantiate the App from the child spec.
    class ChildApp(ChildConfig, App):
        pass

    app = ChildApp()
    # Assertion: the child engine configuration takes precedence.
    assert app.engine is child_engine
