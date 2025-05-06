import pytest
from swarmauri_toolkit_jupytertoolkit import __version__


@pytest.mark.i9n
class TestI9nInit:
    """Tests the package initializer for swarmauri_toolkit_jupytertoolkit."""

    def test_version(self):
        """Ensures that the __version__ is correctly set."""
        assert __version__ != "0.0.0"

    def test_init(self):
        """Ensures that the __init__.py loads correctly."""
        try:
            from swarmauri_toolkit_jupytertoolkit import (
                JupyterToolkit as JupyterToolkit,
            )
        except ImportError:
            pytest.fail("Failed to import JupyterToolkit")

    def test_all(self):
        """Ensures that the __all__ is correctly set."""
        from swarmauri_toolkit_jupytertoolkit import __all__

        assert "JupyterToolkit" in __all__
