from tigrbl import TigrblApp
from tigrbl.app._app import App as InternalApp


def test_app_reexport():
    assert issubclass(TigrblApp, InternalApp)
