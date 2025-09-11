import importlib
import pytest


@pytest.mark.i9n
def test_init_module_import():
    module = importlib.import_module("swarmauri_storage_github")
    assert module is not None


@pytest.mark.i9n
def test_init_module_version():
    module = importlib.import_module("swarmauri_storage_github")
    assert hasattr(module, "__version__")
    assert isinstance(module.__version__, str)
    assert module.__version__


@pytest.mark.i9n
def test_init_module_all_variable():
    module = importlib.import_module("swarmauri_storage_github")
    assert hasattr(module, "__all__")
    assert "GithubStorageAdapter" in module.__all__
