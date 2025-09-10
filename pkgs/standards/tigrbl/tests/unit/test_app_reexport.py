from tigrbl import App
from tigrbl.app._app import App as InternalApp


def test_app_reexport():
    assert App is InternalApp
