from tigrbl.v3 import App
from tigrbl.v3.app._app import App as InternalApp


def test_app_reexport():
    assert App is InternalApp
