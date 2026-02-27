from tigrbl import TigrblApp
from tigrbl._concrete._app import App as InternalApp


def test_app_reexport():
    assert issubclass(TigrblApp, InternalApp)
