from autoapi.v3 import app
from fastapi import FastAPI


def test_app_reexport():
    assert app is FastAPI
