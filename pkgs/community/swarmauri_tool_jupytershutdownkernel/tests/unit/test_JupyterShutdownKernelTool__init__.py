"""Unit tests for the swarmauri_tool_jupytershutdownkernel package initialization.

This test suite ensures that the package's __init__.py properly imports and
exposes the JupyterShutdownKernelTool class, along with other metadata like
the __version__ attribute.
"""

from swarmauri_tool_jupytershutdownkernel import JupyterShutdownKernelTool, __version__


class TestPackageInitialization:
    """Test case class for ensuring the correct exposure of package-level components."""

    def test_jupyter_shutdown_kernel_tool_existence(self) -> None:
        """
        Test that the JupyterShutdownKernelTool class is importable and exposed
        by the package's __init__.py.
        """
        # Checking that JupyterShutdownKernelTool is not None ensures proper import.
        assert JupyterShutdownKernelTool is not None, (
            "JupyterShutdownKernelTool must be exposed by __init__.py."
        )

    def test_version_attribute_existence(self) -> None:
        """
        Test that the __version__ attribute is defined and is a valid string
        within the package's __init__.py.
        """
        # Ensuring that __version__ is a string prevents potential import issues.
        assert isinstance(__version__, str), "__version__ must be a string."
        assert __version__, "__version__ must not be an empty string."
