from unittest.mock import patch, MagicMock
import pytest

from swarmauri_tool_httploaded import HTTPLoadedTool as Tool


MANIFEST = """
name: Example HTTP Tool
description: Example description
parameters:
  - name: p1
    input_type: string
    description: Param 1
    required: true
components:
  - type: CalculatorTool
"""


@pytest.mark.unit
def test_ubc_resource():
    with patch("httpx.get") as mock_get:
        mock_resp = MagicMock(text=MANIFEST)
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp
        tool = Tool(url="http://example.com")
        assert tool.resource == "Tool"


@pytest.mark.unit
def test_ubc_type():
    with patch("httpx.get") as mock_get:
        mock_resp = MagicMock(text=MANIFEST)
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp
        assert Tool(url="http://example.com").type == "HTTPLoadedTool"


@pytest.mark.unit
def test_initialization():
    with patch("httpx.get") as mock_get:
        mock_resp = MagicMock(text=MANIFEST)
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp
        tool = Tool(url="http://example.com")
        assert tool.name == "Example HTTP Tool"
        assert tool.description == "Example description"
        assert len(tool.parameters) == 1
        assert tool.parameters[0].name == "p1"


@pytest.mark.unit
def test_serialization():
    with patch("httpx.get") as mock_get:
        mock_resp = MagicMock(text=MANIFEST)
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp
        tool = Tool(url="http://example.com")
        copy = Tool.model_validate_json(tool.model_dump_json())
        assert copy.url == tool.url
        assert copy.name == tool.name


@pytest.mark.unit
def test_call():
    with patch("httpx.get") as mock_get:
        mock_resp = MagicMock(text=MANIFEST)
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp
        tool = Tool(url="http://example.com")
        result = tool()
        assert len(result) == 1
        assert result[0].type == "CalculatorTool"
        mock_get.assert_called_with("http://example.com", headers=None)
