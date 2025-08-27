from autoapi.v3 import App
from autoapi.v3.deps.fastapi import App as FastAPIApp


def test_app_reexport():
    assert App is FastAPIApp
