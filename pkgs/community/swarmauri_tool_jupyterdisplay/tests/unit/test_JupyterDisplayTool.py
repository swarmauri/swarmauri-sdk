import pytest
from unittest.mock import patch, MagicMock
from swarmauri_tool_jupyterdisplay.JupyterDisplayTool import JupyterDisplayTool


@pytest.fixture
def jupyter_display_tool() -> JupyterDisplayTool:
    """
    Pytest fixture to instantiate a JupyterDisplayTool object.

    Returns:
        JupyterDisplayTool: A new instance of JupyterDisplayTool.
    """
    return JupyterDisplayTool()


def test_jupyter_display_tool_instantiate(
    jupyter_display_tool: JupyterDisplayTool,
) -> None:
    """
    Tests basic instantiation of JupyterDisplayTool and checks
    that the default attributes match expected values.
    """
    assert jupyter_display_tool.name == "JupyterDisplayTool"
    assert jupyter_display_tool.version == "1.0.0"
    assert jupyter_display_tool.type == "JupyterDisplayTool"
    assert len(jupyter_display_tool.parameters) == 2


@patch("IPython.display.display")
def test_jupyter_display_tool_call_text(
    mock_display: MagicMock, jupyter_display_tool: JupyterDisplayTool
) -> None:
    """
    Tests calling the JupyterDisplayTool with plain text data_format.
    Verifies that the response includes a success status and that the display function is called.
    """
    data = "Hello, world!"
    response = jupyter_display_tool(data, data_format="text")

    assert response["status"] == "success"
    assert "successfully" in response["message"].lower()
    mock_display.assert_called_once()


@patch("IPython.display.display")
def test_jupyter_display_tool_call_html(
    mock_display: MagicMock, jupyter_display_tool: JupyterDisplayTool
) -> None:
    """
    Tests calling the JupyterDisplayTool with HTML data_format.
    Verifies that the response includes a success status and that the display function is called.
    """
    data = "<b>Hello, HTML!</b>"
    response = jupyter_display_tool(data, data_format="html")

    assert response["status"] == "success"
    assert "successfully" in response["message"].lower()
    mock_display.assert_called_once()


@patch("IPython.display.display")
def test_jupyter_display_tool_call_latex(
    mock_display: MagicMock, jupyter_display_tool: JupyterDisplayTool
) -> None:
    """
    Tests calling the JupyterDisplayTool with LaTeX data_format.
    Verifies that the response includes a success status and that the display function is called.
    """
    data = r"\frac{1}{2} \text{ is a fraction.}"
    response = jupyter_display_tool(data, data_format="latex")

    assert response["status"] == "success"
    assert "successfully" in response["message"].lower()
    mock_display.assert_called_once()


@patch("IPython.display.display")
def test_jupyter_display_tool_call_image(
    mock_display: MagicMock, jupyter_display_tool: JupyterDisplayTool
) -> None:
    """
    Tests calling the JupyterDisplayTool with image data_format.
    Verifies that the response includes a success status and that the display function is called.
    """
    data = "test_image.png"
    response = jupyter_display_tool(data, data_format="image")

    assert response["status"] == "success"
    assert "successfully" in response["message"].lower()
    mock_display.assert_called_once()


@patch("IPython.display.display")
def test_jupyter_display_tool_call_auto(
    mock_display: MagicMock, jupyter_display_tool: JupyterDisplayTool
) -> None:
    """
    Tests calling the JupyterDisplayTool with the default (auto) data_format.
    In this scenario, it should treat the data as text and display it accordingly.
    """
    data = "Auto-detected text content."
    response = jupyter_display_tool(data)

    assert response["status"] == "success"
    assert "successfully" in response["message"].lower()
    mock_display.assert_called_once()


@patch("IPython.display.display")
def test_jupyter_display_tool_call_error(
    mock_display: MagicMock, jupyter_display_tool: JupyterDisplayTool
) -> None:
    """
    Tests error handling in the JupyterDisplayTool by causing an exception to be raised
    during display. Verifies that an error response is returned.
    """
    mock_display.side_effect = Exception("Display function error")
    data = "This will cause an exception."
    response = jupyter_display_tool(data, data_format="text")

    assert response["status"] == "error"
    assert "error" in response["message"].lower()
