import importlib
import logging

import pytest


logger = logging.getLogger(__name__)


@pytest.mark.i9n
class TestInit:
    """Integration tests for package initialization."""

    def test_module_import(self):
        """Module can be imported."""
        module = importlib.import_module("swarmauri_crypto_composite")
        assert module is not None

    def test_version(self):
        """__version__ is exposed and non-empty."""
        module = importlib.import_module("swarmauri_crypto_composite")
        assert isinstance(module.__version__, str)
        assert module.__version__

    def test_all_and_class(self):
        """__all__ lists CompositeCrypto and it is exposed."""
        module = importlib.import_module("swarmauri_crypto_composite")
        assert "CompositeCrypto" in module.__all__
        assert hasattr(module, "CompositeCrypto")
