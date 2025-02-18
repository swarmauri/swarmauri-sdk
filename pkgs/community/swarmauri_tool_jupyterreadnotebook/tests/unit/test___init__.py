# swarmauri_tool_jupyterreadnotebook/tests/unit/test___init__.py

"""
Module containing unit tests for the initialization of the
swarmauri_tools_jupyterreadnotebook package.
"""

import pytest
from swarmauri_base.tools.ToolBase import ToolBase


class TestPackageInitialization:
    """
    Class containing tests for the initialization of the
    swarmauri_tools_jupyterreadnotebook package.
    """

    def test_jupyter_read_notebook_tool_import(self) -> None:
        """
        Test that JupyterReadNotebookTool is successfully imported from the package's __init__.
        """
        from swarmauri_tool_jupyterreadnotebook import JupyterReadNotebookTool

        # Verify we can access the class
        assert JupyterReadNotebookTool is not None, (
            "JupyterReadNotebookTool should be imported from the package init file."
        )

    def test_package_version(self) -> None:
        """
        Test that the package __version__ string is available and non-empty.
        """
        from swarmauri_tool_jupyterreadnotebook import __version__

        # Verify the version is a non-empty string
        assert isinstance(__version__, str), "__version__ should be a string."
        assert len(__version__) > 0, "__version__ should not be an empty string."

    @pytest.mark.skip(
        reason="Example test for demonstration of base class inheritance."
    )
    def test_jupyter_read_notebook_tool_inherits_correctly(self) -> None:
        """
        Test that JupyterReadNotebookTool inherits from the expected base class.
        This test is provided as an example if there is a known base class to check against.
        """
        from swarmauri_tool_jupyterreadnotebook import JupyterReadNotebookTool

        # Here we check only as an example scenario; adjust accordingly for real use.
        assert issubclass(JupyterReadNotebookTool, ToolBase) is False, (
            "Inherit from ToolBase if JupyterReadNotebookTool must extend a known base class."
        )
