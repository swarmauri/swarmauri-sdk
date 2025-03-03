"""
test_JupyterClearOutputTool.py

This module provides test coverage for the JupyterClearOutputTool, ensuring it properly clears
outputs from Jupyter notebooks and adheres to its defined interface.
"""

import pytest
from typing import Dict, Any

from swarmauri_tool_jupyterclearoutput.JupyterClearOutputTool import (
    JupyterClearOutputTool,
)


@pytest.fixture
def sample_notebook() -> Dict[str, Any]:
    """
    Returns a sample Jupyter notebook structure containing both code and markdown cells,
    with some predefined outputs in the code cells.
    """
    return {
        "cells": [
            {
                "cell_type": "code",
                "execution_count": 1,
                "metadata": {},
                "outputs": [{"output_type": "stream", "text": "Hello World\n"}],
                "source": ["print('Hello World')"],
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": ["# This is a markdown cell"],
            },
            {
                "cell_type": "code",
                "execution_count": 2,
                "metadata": {},
                "outputs": [
                    {"output_type": "execute_result", "data": {"text/plain": "2"}}
                ],
                "source": ["2"],
            },
        ],
        "metadata": {"language_info": {"name": "python"}},
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def test_tool_instantiation() -> None:
    """
    Tests whether the JupyterClearOutputTool can be instantiated with its default parameters.
    """
    tool = JupyterClearOutputTool()
    assert tool is not None, "Tool instantiation failed."


def test_tool_attributes() -> None:
    """
    Checks the default attribute values of the JupyterClearOutputTool.
    """
    tool = JupyterClearOutputTool()
    assert tool.version == "1.0.0", "Version does not match expected default."
    assert tool.name == "JupyterClearOutputTool", (
        "Name does not match expected default."
    )
    assert tool.type == "JupyterClearOutputTool", (
        "Type does not match expected default."
    )
    assert len(tool.parameters) > 0, "Tool parameters should not be empty."


def test_clearing_outputs(sample_notebook: Dict[str, Any]) -> None:
    """
    Verifies that the tool removes outputs and resets execution counts from all code cells
    while preserving the original cell code and metadata.
    """
    tool = JupyterClearOutputTool()
    cleaned_notebook = tool(sample_notebook)

    # Check that code cells have had their outputs cleared.
    code_cells = [
        cell
        for cell in cleaned_notebook.get("cells", [])
        if cell.get("cell_type") == "code"
    ]
    for cell in code_cells:
        assert cell.get("outputs") == [], "Outputs were not cleared from a code cell."
        assert cell.get("execution_count") is None, "Execution count was not reset."

    # Verify that markdown cells remain unchanged.
    markdown_cells = [
        cell
        for cell in cleaned_notebook.get("cells", [])
        if cell.get("cell_type") == "markdown"
    ]
    assert len(markdown_cells) == 1, "Unexpected number of markdown cells."
    original_markdown_cell = sample_notebook["cells"][1]
    updated_markdown_cell = markdown_cells[0]
    assert updated_markdown_cell["source"] == original_markdown_cell["source"], (
        "Markdown cell content was unexpectedly modified."
    )


def test_clearing_with_no_cells() -> None:
    """
    Ensures that the tool handles a notebook with no cells without errors.
    The notebook dict should remain structurally the same, minus any alterations to cells.
    """
    tool = JupyterClearOutputTool()
    empty_notebook = {"cells": [], "metadata": {}, "nbformat": 4, "nbformat_minor": 5}
    cleaned_notebook = tool(empty_notebook)

    assert "cells" in cleaned_notebook, "Cleaned notebook is missing the 'cells' key."
    assert len(cleaned_notebook["cells"]) == 0, "Cells should remain empty."
    assert cleaned_notebook["metadata"] == {}, "Metadata should remain unchanged."


def test_clearing_with_only_markdown_cells() -> None:
    """
    Validates correct behavior when the notebook has only markdown cells.
    No outputs should be cleared since there are no code cells.
    """
    tool = JupyterClearOutputTool()
    markdown_only_notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": ["# Just a heading in markdown"],
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": ["Some more markdown content."],
            },
        ],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    cleaned_notebook = tool(markdown_only_notebook)

    for cell in cleaned_notebook["cells"]:
        assert cell["cell_type"] == "markdown", "Cell type should remain markdown."
        assert "outputs" not in cell, "Markdown cells should not contain any outputs."
        assert cell["source"] is not None, "Markdown cell content should be preserved."


def test_parameters_structure() -> None:
    """
    Ensures that the tool's parameters are properly defined and contain the required fields.
    """
    tool = JupyterClearOutputTool()
    assert len(tool.parameters) == 1, "There should be exactly one parameter defined."
    param = tool.parameters[0]
    assert param.name == "notebook_data", (
        "Parameter name does not match expected value."
    )
    assert param.input_type == "object", "Parameter type does not match expected value."
    assert param.required, "Parameter should be required."
    assert "A dictionary that represents" in param.description, (
        "Parameter description is missing or incomplete."
    )
