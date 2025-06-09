import importlib
import pytest


@pytest.mark.i9n
def test_init_module_import():
    module = importlib.import_module("swarmauri_middleware_jsonrpc")
    assert hasattr(module, "JsonRpcMiddleware")
    assert "JsonRpcMiddleware" in module.__all__
    assert isinstance(module.__version__, str)
