import importlib

import pytest


@pytest.mark.unit
def test_package_module_importable() -> None:
    module = importlib.import_module("tigrbl_concrete._concrete")

    assert module is not None
