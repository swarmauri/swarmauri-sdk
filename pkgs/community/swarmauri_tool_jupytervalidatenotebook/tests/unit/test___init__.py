"""
Unit tests for the swarmauri_tool_jupytervalidatenotebook package initialization.

This module includes unittest-based test cases for verifying the initialization of
the swarmauri_tool_jupytervalidatenotebook package. It ensures that the __init__.py
file correctly exposes the JupyterValidateNotebookTool class and the __version__ attribute.
"""

import unittest
from swarmauri_tool_jupytervalidatenotebook import JupyterValidateNotebookTool, __version__


class TestInit(unittest.TestCase):
    """
    Contains test cases for the package initialization.
    Ensures the __init__.py file correctly exposes the JupyterValidateNotebookTool class.
    """

    def test_import_tool(self) -> None:
        """
        Test that the JupyterValidateNotebookTool is properly importable from the package.
        """
        # Check that the imported object is indeed a class.
        self.assertTrue(callable(JupyterValidateNotebookTool), "JupyterValidateNotebookTool should be callable")

    def test_instantiate_tool(self) -> None:
        """
        Test that an instance of JupyterValidateNotebookTool can be created.
        """
        # Creating an instance to ensure the class is functional.
        tool_instance = JupyterValidateNotebookTool()
        self.assertIsNotNone(tool_instance, "Failed to instantiate JupyterValidateNotebookTool")

    def test_version_attribute(self) -> None:
        """
        Test that the __version__ attribute is properly exposed and valid.
        """
        # Ensure __version__ is a non-empty string.
        self.assertIsInstance(__version__, str, "__version__ should be a string")
        self.assertGreater(len(__version__), 0, "__version__ string should not be empty")