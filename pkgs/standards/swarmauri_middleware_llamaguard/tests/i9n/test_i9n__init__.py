import logging
from importlib import import_module

import pytest


@pytest.mark.i9n
class TestInit:
    """Tests for the package initializer."""

    def test_version(self):
        """Tests that the package version is correctly loaded."""
        mod = import_module("swarmauri_middleware_llamaguard")
        try:
            version = mod.__version__
            assert isinstance(version, str), "Version must be a string"
        except AttributeError:
            logging.error("Package version not found. Is the package installed?")
            pytest.fail("Package version not found")

    def test_all(self):
        """Tests that __all__ is correctly defined."""
        mod = import_module("swarmauri_middleware_llamaguard")
        assert hasattr(mod, "__all__"), "__all__ not found in package"
        assert isinstance(mod.__all__, list), "__all__ must be a list"
        assert mod.__all__ == ["LlamaGuardMiddleware"], (
            "__all__ contains unexpected values"
        )

    def test_llamaguardmiddleware_import(self):
        """Tests that LlamaGuardMiddleware is properly imported."""
        mod = import_module("swarmauri_middleware_llamaguard")
        from swarmauri_middleware_llamaguard import LlamaGuardMiddleware

        assert hasattr(mod, "LlamaGuardMiddleware"), "LlamaGuardMiddleware not found"
        assert isinstance(LlamaGuardMiddleware, type), (
            "LlamaGuardMiddleware is not a class"
        )


@pytest.fixture
def middleware_class():
    """Fixture to provide the LlamaGuardMiddleware class."""
    from swarmauri_middleware_llamaguard import LlamaGuardMiddleware

    return LlamaGuardMiddleware


@pytest.mark.i9n
def test_no_unexpected_exports(middleware_class):
    """Tests that only expected classes are exported."""
    mod = import_module("swarmauri_middleware_llamaguard")
    assert len(mod.__all__) == 1, "Unexpected number of exported items"
