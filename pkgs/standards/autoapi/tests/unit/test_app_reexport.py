from autoapi.v3 import App
from fastapi import FastAPI


def test_app_reexport():
    assert App is FastAPI
