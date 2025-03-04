"""
This file contains pytest-based unit tests for verifying the package initialization of
swarmauri_tool_jupyterexportpython. It checks that the JupyterExportPythonTool class
is correctly exposed by the package's __init__.py file and that the version attribute
is properly set.
"""

from swarmauri_tool_jupyterexportpython import JupyterExportPythonTool, __version__


class TestInit:
    """
    A pytest-based test class that verifies the package initialization
    of swarmauri_tool_jupyterexportpython.
    """

    def test_jupyter_export_python_tool_import(self) -> None:
        """
        Test whether JupyterExportPythonTool can be imported from the package.
        """
        assert JupyterExportPythonTool is not None, (
            "JupyterExportPythonTool should be exposed by the package's __init__.py"
        )

    def test_jupyter_export_python_tool_is_class(self) -> None:
        """
        Test whether JupyterExportPythonTool is a class.
        """
        assert isinstance(JupyterExportPythonTool, type), (
            "JupyterExportPythonTool should be a class."
        )

    def test_version_attribute(self) -> None:
        """
        Test whether __version__ is defined and is a non-empty string.
        """
        assert isinstance(__version__, str), "__version__ should be a string."
        assert len(__version__) > 0, "__version__ should not be an empty string."

    def test_all_contains_tool(self) -> None:
        """
        Ensure that JupyterExportPythonTool is listed in the __all__ attribute of the package.
        """
        import swarmauri_tool_jupyterexportpython

        assert hasattr(swarmauri_tool_jupyterexportpython, "__all__"), (
            "__all__ attribute not found in the package's __init__.py."
        )
        assert (
            "JupyterExportPythonTool" in swarmauri_tool_jupyterexportpython.__all__
        ), "JupyterExportPythonTool not found in __all__."
